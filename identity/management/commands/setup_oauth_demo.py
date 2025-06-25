from django.core.management.base import BaseCommand
from oauth2_provider.models import Application


class Command(BaseCommand):
    help = 'Setup OAuth2 client application for "Login with ContextID"'

    def handle(self, *args, **options):
        # Check if ContextID application already exists
        try:
            app = Application.objects.get(client_id='contextid-client')
            self.stdout.write(
                self.style.WARNING('ContextID OAuth2 application already exists')
            )
            return
        except Application.DoesNotExist:
            pass

        # Create ContextID OAuth2 application with multiple redirect URIs for different ports
        redirect_uris = "\n".join([
            "http://127.0.0.1:8000/oauth/callback/",
            "http://localhost:8000/oauth/callback/",
            "http://127.0.0.1:8080/oauth/callback/",
            "http://localhost:8080/oauth/callback/",
            "http://127.0.0.1:8081/oauth/callback/",
            "http://localhost:8081/oauth/callback/",
        ])
        
        app = Application.objects.create(
            name="ContextID Client",
            client_id="contextid-client",
            client_secret="contextid-secret-key",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris=redirect_uris,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created ContextID OAuth2 application:\n'
                f'Client ID: {app.client_id}\n'
                f'Client Secret: {app.client_secret}\n'
                f'Redirect URIs: {app.redirect_uris}'
            )
        )