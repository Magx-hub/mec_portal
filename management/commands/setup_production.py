from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Setup production environment'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write('Setting up production...')
            
            # Collect static files
            call_command('collectstatic', '--noinput')
            
            # Run migrations
            call_command('migrate')
            
            # Create superuser if needed
            if not settings.AUTH_USER_MODEL.objects.filter(is_superuser=True).exists():
                self.stdout.write('Creating superuser...')
                call_command('createsuperuser')
            
            self.stdout.write(
                self.style.SUCCESS('Production setup completed!')
            )
        else:
            self.stdout.write(
                self.style.ERROR('This command should only be run in production')
            )