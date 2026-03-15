#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time


# Commands that need a live DB connection.
# During Render BUILD phase, the internal Postgres hostname isn't reachable.
# During START phase it is reachable but may take a few seconds to be ready.
_DB_COMMANDS = {"migrate", "create_admin"}

_DB_ERROR_HINTS = (
    "Name or service not known",
    "could not translate host name",
    "Connection refused",
    "could not connect to server",
    "the database system is starting up",
    "remaining connection slots are reserved",
)

MAX_RETRIES = 15  # Up to 90 seconds
RETRY_DELAY = 6   # seconds between retries


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

    if cmd in _DB_COMMANDS:
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                execute_from_command_line(sys.argv)
                last_exc = None
                break  # success — stop retrying
            except Exception as exc:
                err = str(exc)
                if any(hint in err for hint in _DB_ERROR_HINTS):
                    last_exc = exc
                    if attempt < MAX_RETRIES:
                        print(
                            f"⚠️  DB not ready (attempt {attempt}/{MAX_RETRIES}), "
                            f"retrying in {RETRY_DELAY}s…"
                        )
                        time.sleep(RETRY_DELAY)
                    else:
                        print(
                            f"\n❌ DB still unreachable after {MAX_RETRIES} attempts.\n"
                            "   If you are in the START phase and this keeps failing,\n"
                            "   try switching DATABASE_URL to the EXTERNAL Database URL\n"
                            "   from your Render Postgres dashboard.\n"
                        )
                        # We still exit 0 to allow gunicorn to at least try to start
                        # in case this is a transient build-time check.
                        sys.exit(0)
                else:
                    raise  # non-connection error — propagate immediately
        if last_exc is not None:
            # We already printed the help message above
            pass
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
