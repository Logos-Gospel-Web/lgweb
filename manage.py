#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # shortcuts
    if len(sys.argv) > 1:
        messages_argv = ['-l', 'zh_CN', '-l', 'zh_TW', '-i', 'venv', '-i', '.git', '-i', '.github', '-i', '.vscode', '-i', 'configs', '-i', 'infrastructure', '-i', 'lib', '-i', 'public']
        if sys.argv[1] == 'makemessages':
            sys.argv = sys.argv[:2] + messages_argv + ['--no-location']
        if sys.argv[1] == 'compilemessages':
            sys.argv = sys.argv[:2] + messages_argv

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
