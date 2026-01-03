from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = "Create admin user if not exists"

    def handle(self, *args, **kwargs):
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        email = os.environ.get("ADMIN_EMAIL", "")

        if not username or not password:
            self.stdout.write("Admin env vars not set")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin already exists")
            return

        User.objects.create_superuser(
            username=username,
            password=password,
            email=email
        )

        self.stdout.write("Admin created")
        