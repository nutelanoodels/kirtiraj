#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# Commands that require a live database connection.
# During Render's BUILD phase, the internal Postgres hostname
# (dpg-xxx-a) is not yet resolvable. We catch connection errors
# for these commands so the build doesn't fail.
# At runtime the DB is reachable and everything works normally.
_DB_COMMANDS = {"migrate", "create_admin"}

_DB_ERROR_HINTS = (
    "Name or service not known",
    "could not translate host name",
    "Connection refused",
    "could not connect to server",
)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    cmd = sys.argv[1] if len(sys.argv) > 1 else ""

    try:
        execute_from_command_line(sys.argv)
    except Exception as exc:
        err = str(exc)
        if cmd in _DB_COMMANDS and any(hint in err for hint in _DB_ERROR_HINTS):
            print(
                f"\n⚠️  Skipping '{cmd}' — database not reachable during build.\n"
                "   This is normal on Render. The command will run automatically\n"
                "   once the service starts via the start command.\n"
            )
            sys.exit(0)   # exit 0 so the build step succeeds
        raise


if __name__ == '__main__':
    main()
