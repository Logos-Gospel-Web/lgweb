#!/usr/bin/env python3

import argparse
import sys
from collections import Counter

from normalize_audio import (
    AUDIO_PREFIX,
    BACKUP_PREFIX,
    create_client,
    load_cache,
    require_env,
    save_cache,
)


def list_backups(s3, bucket):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=BACKUP_PREFIX):
        for item in page.get('Contents', []):
            key = item['Key']
            if key.endswith('/'):
                continue
            yield key, int(item['Size'])


def process(args):
    bucket = require_env('S3_BUCKET_NAME')
    s3 = create_client()
    cache = load_cache(s3, bucket)
    backups = list(list_backups(s3, bucket))
    summary = Counter()
    failures = []

    for index, (backup_key, size) in enumerate(backups, start=1):
        prefix = f'[{index}/{len(backups)}]'
        audio_key = AUDIO_PREFIX + backup_key[len(BACKUP_PREFIX):]

        if args.dry_run:
            summary['would_restore'] += 1
            print(
                f'{prefix} WOULD RESTORE {audio_key} '
                f'({size} bytes from {backup_key})',
                flush=True,
            )
            continue

        try:
            s3.copy_object(
                Bucket=bucket,
                Key=audio_key,
                CopySource={'Bucket': bucket, 'Key': backup_key},
                MetadataDirective='COPY',
            )
            if audio_key in cache:
                del cache[audio_key]
                save_cache(s3, bucket, cache)

            deleted = ''
            if args.delete_backups:
                s3.delete_object(Bucket=bucket, Key=backup_key)
                deleted = f', backup {backup_key} deleted'

            summary['restored'] += 1
            print(
                f'{prefix} RESTORED {audio_key} '
                f'({size} bytes from {backup_key}{deleted})',
                flush=True,
            )
        except Exception as error:
            summary['failed'] += 1
            failures.append((audio_key, str(error)))
            print(f'{prefix} FAILED {audio_key}: {error}', file=sys.stderr, flush=True)

    print('\nSummary:', flush=True)
    for name in ('restored', 'would_restore', 'failed'):
        print(f'  {name}: {summary[name]}', flush=True)

    if failures:
        print('\nFailures:', file=sys.stderr, flush=True)
        for key, error in failures:
            print(f'  {key}: {error}', file=sys.stderr, flush=True)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Restore audio under message/audio/ from message/audio_backup/.'
    )
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--delete-backups', action='store_true')
    return process(parser.parse_args())


if __name__ == '__main__':
    sys.exit(main())
