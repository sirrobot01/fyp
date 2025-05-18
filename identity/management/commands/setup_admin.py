from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from identity.models import UserRole


class Command(BaseCommand):
    help = 'Setup admin user with proper roles'

    def handle(self, *args, **options):
        # Create admin user if doesn't exist
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write('Created admin user')

        # Ensure profile exists
        profile, created = UserRole.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'can_manage_users': True,
                'can_view_all_identities': True
            }
        )

        self.stdout.write('Admin setup complete')