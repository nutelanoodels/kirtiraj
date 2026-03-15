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

MAX_RETRIES = 5
RETRY_DELAY = 4  # seconds between retries


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
                        # Exhausted retries — if this is the build phase,
                        # exit 0 so collectstatic can still run.
                        # At runtime the DB should always be reachable.
                        print(
                            f"\n⚠️  DB still unreachable after {MAX_RETRIES} attempts.\n"
                            f"   Skipping '{cmd}' (likely build phase).\n"
                        )
                        sys.exit(0)
                else:
                    raise  # non-connection error — propagate immediately
        if last_exc is not None:
            raise last_exc
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
