import argparse
import cairosvg
import django
from django.conf import settings
from django.template.loader import get_template
from pathlib import Path
from app.lang import LANGUAGES
import hashlib
import json
import sys

_templates = [
    'site/prerendered/base_head.html',
    'site/prerendered/base_body.html',
    'site/prerendered/error_head.html',
    'site/prerendered/statistics_head.html',
    'site/prerendered/webmanifest.json',
]

def _generate_png(input: str, size: int, output: Path):
    cairosvg.svg2png(
        bytestring=input,
        write_to=str(output),
        output_width=size,
        output_height=size
    )

def _generate_favicons(output_dir: Path):
    icon_template = get_template(f'site/prerendered/favicons/any')
    maskable_template = get_template(f'site/prerendered/favicons/maskable')
    rounded_template = get_template(f'site/prerendered/favicons/rounded')
    contexts = { lang: { 'text_template': f'./{lang}' } for lang in LANGUAGES }
    icons = { lang: icon_template.render(context) for lang, context in contexts.items() }
    maskables = { lang: maskable_template.render(context) for lang, context in contexts.items() }
    roundeds = { lang: rounded_template.render(context) for lang, context in contexts.items() }

    hasher = hashlib.sha256()
    for svg in icons.values():
        hasher.update(svg.encode())
    for svg in maskables.values():
        hasher.update(svg.encode())
    for svg in roundeds.values():
        hasher.update(svg.encode())
    favicon_hash = hasher.hexdigest()[:8]

    for lang in LANGUAGES:
        icon = icons[lang]
        maskable = maskables[lang]
        rounded = roundeds[lang]

        out_dir = output_dir / lang / favicon_hash
        out_dir.mkdir(parents=True, exist_ok=True)

        _generate_png(icon, 180, out_dir / 'apple-touch-icon.png')
        _generate_png(icon, 192, out_dir / 'favicon-192.png')
        _generate_png(icon, 512, out_dir / 'favicon-512.png')
        _generate_png(maskable, 512, out_dir / 'favicon-maskable.png')

        (out_dir / 'favicon.svg').write_text(rounded)

    return favicon_hash

def _read_manifest(manifest_file: Path):
    if not manifest_file.is_file():
        sys.exit(f'"{manifest_file}" does not exist.')
    text = manifest_file.read_text()
    try:
        return json.loads(text)
    except:
        sys.exit(f'"{manifest_file}" is not a valid json.')

def _generate_single_template(template_path: str, context: dict[str, str]):
    template = get_template(template_path)
    return (template.origin.name, template.render(context))

def _generate_templates(context: dict[str, str]):
    return [_generate_single_template(t, context) for t in _templates]

def _setup(template_dir: str):
    settings.configure(
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [template_dir],
                'APP_DIRS': False,
            },
        ]
    )
    django.setup()

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        type=str,
        required=False,
        default=None,
        help="Template directory"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        default=None,
        help="Output directory"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        required=False,
        default=None,
        help="Manifest json from asset compilation"
    )
    parser.add_argument(
        "--dry-run",
        action='store_true',
        default=False,
        help="Do not write to prerendered template folder"
    )
    return parser.parse_args()

def main():
    args = _parse_args()
    template_dir: str | None = args.base
    _setup(template_dir)
    manifest_file: str | None = args.manifest
    output_dir: str | None  = args.output
    dry_run: bool = args.dry_run

    context: dict[str, str] = {
        'language': '{{ language }}',
        'base_title': '{{ base_title }}',
    }

    if manifest_file:
        manifest = _read_manifest(Path(manifest_file))
        context['js_script'] = manifest['script.js'].strip('/')
        context['js_sw'] = manifest['sw.js'].strip('/')
        context['css_style'] = manifest['style.css'].strip('/')
        context['css_noscript'] = manifest['noscript.css'].strip('/')
        context['css_error'] = manifest['error.css'].strip('/')
        context['css_statistics'] = manifest['statistics.css'].strip('/')
    else:
        context['js_script'] = '{{ js_script }}'
        context['js_sw'] = '{{ js_sw }}'
        context['css_style'] = '{{ css_style }}'
        context['css_noscript'] = '{{ css_noscript }}'
        context['css_error'] = '{{ css_error }}'
        context['css_statistics'] = '{{ css_statistics }}'

    if output_dir:
        favicon_hash = _generate_favicons(Path(output_dir))
        context['favicon_hash'] = favicon_hash
    else:
        context['favicon_hash'] = '{{ favicon_hash }}'

    templates = _generate_templates(context)

    if dry_run:
        print(templates)
    else:
        for template_path, content in templates:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

if __name__ == '__main__':
    main()
