from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from identity.models import Identity
import random


class Command(BaseCommand):
    help = 'Create sample identity data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Number of users to create')

    def handle(self, *args, **options):
        users_count = options['users']

        contexts = ['legal', 'display', 'social', 'professional', 'username']
        visibilities = ['public', 'friends', 'private', 'organization']

        sample_names = [
            ('John', 'Doe'), ('Jane', 'Smith'), ('Alex', 'Johnson'),
            ('Maria', 'Garcia'), ('David', 'Brown'), ('Sarah', 'Wilson'),
            ('Michael', 'Taylor'), ('Emily', 'Anderson'), ('Robert', 'Thomas'),
            ('Lisa', 'Jackson')
        ]

        for i in range(users_count):
            # Create user
            username = f'user{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': sample_names[i % len(sample_names)][0],
                    'last_name': sample_names[i % len(sample_names)][1]
                }
            )

            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {username}')

            # Create identities for different contexts
            for j, context in enumerate(contexts[:3]):  # Create 3 identities per user
                identity, created = Identity.objects.get_or_create(
                    user=user,
                    context=context,
                    defaults={
                        'given_name': user.first_name,
                        'family_name': user.last_name,
                        'email': user.email if context != 'username' else '',
                        'visibility': random.choice(visibilities),
                        'is_primary': j == 0,  # First identity is primary
                        'pronouns': random.choice(['they/them', 'she/her', 'he/him']),
                        'bio': f'Sample bio for {context} context',
                        'custom_attributes': {
                            'department': 'Engineering' if context == 'professional' else '',
                            'hobby': 'Reading' if context == 'social' else ''
                        }
                    }
                )

                if created:
                    self.stdout.write(f'Created {context} identity for {username}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data for {users_count} users')
        )