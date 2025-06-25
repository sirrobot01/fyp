from django.core.management.base import BaseCommand
from oauth2_provider.models import Application


class Command(BaseCommand):
    help = 'Update ContextID OAuth2 client application'

    def handle(self, *args, **options):
        # Update or create ContextID application
        redirect_uris = "\n".join([
            "http://127.0.0.1:8000/oauth/callback/",
            "http://localhost:8000/oauth/callback/",
            "http://127.0.0.1:8080/oauth/callback/",
            "http://localhost:8080/oauth/callback/",
            "http://127.0.0.1:8081/oauth/callback/",
            "http://localhost:8081/oauth/callback/",
        ])
        
        # Delete old demo app if it exists
        Application.objects.filter(client_id="demo-client-id").delete()
        
        app, created = Application.objects.update_or_create(
            client_id="contextid-client",
            defaults={
                "name": "ContextID Client",
                "client_secret": "contextid-secret-key",
                "client_type": Application.CLIENT_CONFIDENTIAL,
                "authorization_grant_type": Application.GRANT_AUTHORIZATION_CODE,
                "redirect_uris": redirect_uris,
            }
        )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} ContextID OAuth2 application:\n'
                f'Client ID: {app.client_id}\n'
                f'Client Secret: {app.client_secret}\n'
                f'Redirect URIs:\n{app.redirect_uris}'
            )
        )