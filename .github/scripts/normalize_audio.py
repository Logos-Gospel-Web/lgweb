#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

AUDIO_PREFIX = 'message/audio/'
BACKUP_PREFIX = 'message/audio_backup/'
CACHE_KEY = 'message/audio-cache.json'
MAX_SAMPLE_RATE = 22050
TARGET_BITRATE = 32000
MAX_ACCEPTED_BITRATE = 35200
MIN_BITRATE = 8000
SUPPORTED_CONTENT_TYPES = {'.mp3': 'audio/mpeg'}
VALID_SAMPLE_RATES = (8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000)


def require_env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f'{name} is required')
    return value


def create_client():
    return boto3.client(
        's3',
        endpoint_url=require_env('S3_ENDPOINT_URL'),
        aws_access_key_id=require_env('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=require_env('S3_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('S3_REGION') or 'auto',
        config=Config(
            signature_version='s3v4',
            retries={'max_attempts': 5, 'mode': 'standard'},
        ),
    )


def is_not_found(error):
    response = getattr(error, 'response', {})
    code = str(response.get('Error', {}).get('Code', ''))
    status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    return code in {'404', 'NoSuchKey', 'NotFound'} or status == 404


def load_cache(s3, bucket):
    try:
        response = s3.get_object(Bucket=bucket, Key=CACHE_KEY)
        data = json.loads(response['Body'].read())
        files = data.get('files')
        if not isinstance(files, dict):
            raise ValueError('cache files must be an object')
        return {key: value for key, value in files.items() if isinstance(value, dict)}
    except ClientError as error:
        if is_not_found(error):
            return {}
        raise
    except ValueError as error:
        print(f'WARNING: ignoring invalid cache {CACHE_KEY}: {error}', file=sys.stderr)
        return {}


def save_cache(s3, bucket, files):
    body = json.dumps(
        {'version': 1, 'files': files},
        ensure_ascii=False,
        sort_keys=True,
    ).encode('utf-8')
    s3.put_object(
        Bucket=bucket,
        Key=CACHE_KEY,
        Body=body,
        ContentType='application/json',
    )


def list_audio(s3, bucket):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=AUDIO_PREFIX):
        for item in page.get('Contents', []):
            key = item['Key']
            if key.endswith('/'):
                continue
            yield key, int(item['Size'])


def probe(path):
    result = subprocess.run(
        [
            'ffprobe', '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,sample_rate,channels,bit_rate:format=duration,bit_rate,size',
            '-of', 'json',
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or 'ffprobe failed')

    data = json.loads(result.stdout or '{}')
    streams = data.get('streams') or []
    if not streams:
        raise RuntimeError('no audio stream found')

    stream = streams[0]
    fmt = data.get('format') or {}
    sample_rate = int(stream.get('sample_rate') or 0)
    channels = int(stream.get('channels') or 0)
    bitrate = int(stream.get('bit_rate') or 0)
    duration = float(fmt.get('duration') or 0)

    if not bitrate:
        if duration > 0:
            size = int(fmt.get('size') or os.path.getsize(path))
            bitrate = round(size * 8 / duration)
        else:
            bitrate = int(fmt.get('bit_rate') or 0)

    return {
        'codec': stream.get('codec_name') or 'unknown',
        'sample_rate': sample_rate,
        'channels': channels,
        'bitrate': bitrate,
        'duration': duration,
    }


def is_compliant(info):
    return (
        0 < info['sample_rate'] <= MAX_SAMPLE_RATE
        and 0 < info['channels'] <= 1
        and 0 < info['bitrate'] <= MAX_ACCEPTED_BITRATE
    )


def choose_sample_rate(sample_rate):
    cap = min(sample_rate or MAX_SAMPLE_RATE, MAX_SAMPLE_RATE)
    valid = [rate for rate in VALID_SAMPLE_RATES if rate <= cap]
    return max(valid) if valid else VALID_SAMPLE_RATES[0]


def choose_bitrate(bitrate):
    return max(MIN_BITRATE, min(bitrate or TARGET_BITRATE, TARGET_BITRATE))


def describe(info):
    return f"{info['sample_rate']} Hz, {info['bitrate'] / 1000:.1f} kbps, {info['channels']} channel(s), {info['codec']}"


def compress(source, output, info):
    sample_rate = choose_sample_rate(info['sample_rate'])
    bitrate = choose_bitrate(info['bitrate'])
    result = subprocess.run(
        [
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
            '-i', str(source),
            '-map', '0:a:0',
            '-vn', '-sn', '-dn',
            '-ac', '1',
            '-ar', str(sample_rate),
            '-c:a', 'libmp3lame',
            '-b:a', str(bitrate),
            '-abr', '1',
            '-map_metadata', '0',
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or 'ffmpeg failed')
    return sample_rate, bitrate


def ensure_backup(s3, bucket, key):
    backup_key = BACKUP_PREFIX + key[len(AUDIO_PREFIX):]
    try:
        s3.head_object(Bucket=bucket, Key=backup_key)
        return backup_key
    except ClientError as error:
        if not is_not_found(error):
            raise

    s3.copy_object(
        Bucket=bucket,
        Key=backup_key,
        CopySource={'Bucket': bucket, 'Key': key},
    )
    return backup_key


def upload_args(head, key):
    content_type = head.get('ContentType')
    if not content_type or content_type in {'application/octet-stream', 'binary/octet-stream'}:
        content_type = SUPPORTED_CONTENT_TYPES.get(Path(key).suffix.lower(), 'application/octet-stream')

    args = {'ContentType': content_type}
    for field in ('CacheControl', 'ContentDisposition', 'ContentLanguage'):
        if head.get(field):
            args[field] = head[field]
    if head.get('Metadata'):
        args['Metadata'] = head['Metadata']
    return args


def cache_entry(size, action):
    return {
        'size': int(size),
        'action': action,
        'checked_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def process(args):
    bucket = require_env('S3_BUCKET_NAME')
    s3 = create_client()
    cache = load_cache(s3, bucket)
    objects = list(list_audio(s3, bucket))
    summary = Counter()
    failures = []
    cache_dirty = False

    seen = set()
    for index, (key, listed_size) in enumerate(objects, start=1):
        prefix = f'[{index}/{len(objects)}]'
        seen.add(key)

        cached = cache.get(key)
        if not args.ignore_cache and cached and cached.get('size') == listed_size:
            summary['cached'] += 1
            print(f'{prefix} SKIP cached {key} ({listed_size} bytes)', flush=True)
            continue

        suffix = Path(key).suffix.lower()
        if suffix not in SUPPORTED_CONTENT_TYPES:
            summary['unsupported'] += 1
            print(f'{prefix} SKIP unsupported extension {key}', flush=True)
            continue

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                source = Path(temp_dir) / f'source{suffix}'
                output = Path(temp_dir) / 'compressed.mp3'

                s3.download_file(bucket, key, str(source))
                info = probe(source)
                summary['checked'] += 1

                if is_compliant(info):
                    summary['compliant'] += 1
                    print(f'{prefix} OK {key} ({describe(info)})', flush=True)
                    if not args.dry_run:
                        cache[key] = cache_entry(listed_size, 'ok')
                        save_cache(s3, bucket, cache)
                        cache_dirty = False
                    continue

                if args.dry_run:
                    summary['would_compress'] += 1
                    print(f'{prefix} WOULD COMPRESS {key} ({describe(info)})', flush=True)
                    continue

                sample_rate, bitrate = compress(source, output, info)
                output_info = probe(output)
                if not is_compliant(output_info):
                    raise RuntimeError(f'verification failed: {describe(output_info)}')

                head = s3.head_object(Bucket=bucket, Key=key)
                backup_key = ensure_backup(s3, bucket, key)
                s3.upload_file(
                    str(output),
                    bucket,
                    key,
                    ExtraArgs=upload_args(head, key),
                )

                output_size = output.stat().st_size
                cache[key] = cache_entry(output_size, 'compressed')
                save_cache(s3, bucket, cache)
                cache_dirty = False
                summary['compressed'] += 1
                print(
                    f'{prefix} COMPRESSED {key} '
                    f'({describe(info)} -> {describe(output_info)}, '
                    f'{listed_size} -> {output_size} bytes, backup {backup_key})',
                    flush=True,
                )
        except Exception as error:
            summary['failed'] += 1
            failures.append((key, str(error)))
            print(f'{prefix} FAILED {key}: {error}', file=sys.stderr, flush=True)

    stale = [
        key for key in cache
        if key.startswith(AUDIO_PREFIX) and key not in seen
    ]
    if stale:
        for key in stale:
            del cache[key]
        cache_dirty = True

    if cache_dirty and not args.dry_run:
        save_cache(s3, bucket, cache)

    print('\nSummary:', flush=True)
    for name in ('checked', 'cached', 'compliant', 'compressed', 'would_compress', 'unsupported', 'failed'):
        print(f'  {name}: {summary[name]}', flush=True)

    if failures:
        print('\nFailures:', file=sys.stderr, flush=True)
        for key, error in failures:
            print(f'  {key}: {error}', file=sys.stderr, flush=True)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description='Normalize audio stored under message/audio/.')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--ignore-cache', action='store_true')
    return process(parser.parse_args())


if __name__ == '__main__':
    sys.exit(main())
