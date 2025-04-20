import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from oauth2_provider.models import Application

from .models import Identity, FieldPermission, UserRole


class IdentityModelTestCase(TestCase):
    """Test cases for the Identity model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
    def test_identity_creation(self):
        """Test creating a basic identity"""
        identity = Identity.objects.create(
            user=self.user,
            context='display',
            given_name='Test',
            family_name='User',
            email='test@example.com'
        )
        
        self.assertEqual(identity.user, self.user)
        self.assertEqual(identity.context, 'display')
        self.assertEqual(identity.given_name, 'Test')
        self.assertEqual(identity.family_name, 'User')
        self.assertTrue(identity.is_active)
        self.assertFalse(identity.is_primary)
        
    def test_get_full_name_display_context(self):
        """Test full name generation for display context"""
        identity = Identity.objects.create(
            user=self.user,
            context='display',
            given_name='John',
            family_name='Doe',
            preferred_name='Johnny',
            title='Mr.',
            suffix='Jr.'
        )
        
        # For display context, should use preferred name if available
        self.assertEqual(identity.get_full_name(), 'Mr. Johnny Doe Jr.')
        
    def test_get_full_name_legal_context(self):
        """Test full name generation for legal context"""
        identity = Identity.objects.create(
            user=self.user,
            context='legal',
            given_name='John',
            family_name='Doe',
            middle_name='William',
            title='Mr.',
            suffix='Jr.'
        )
        
        # For legal context, should include middle name
        self.assertEqual(identity.get_full_name(), 'Mr. John William Doe Jr.')
        
    def test_get_full_name_with_display_name(self):
        """Test full name when display_name is set"""
        identity = Identity.objects.create(
            user=self.user,
            context='social',
            given_name='John',
            family_name='Doe',
            display_name='Johnny D'
        )
        
        # Should use display_name when available
        self.assertEqual(identity.get_full_name(), 'Johnny D')
        
    def test_unique_context_per_user_locale(self):
        """Test that user can only have one identity per context per locale"""
        # Create first identity
        Identity.objects.create(
            user=self.user,
            context='display',
            locale='en-US',
            given_name='Test',
            family_name='User'
        )
        
        # Try to create another with same context and locale
        with self.assertRaises(Exception):
            Identity.objects.create(
                user=self.user,
                context='display',
                locale='en-US',
                given_name='Test2',
                family_name='User2'
            )
            
    def test_different_locales_allowed(self):
        """Test that same context with different locales is allowed"""
        identity1 = Identity.objects.create(
            user=self.user,
            context='display',
            locale='en-US',
            given_name='Test',
            family_name='User'
        )
        
        identity2 = Identity.objects.create(
            user=self.user,
            context='display',
            locale='fr-FR',
            given_name='Teste',
            family_name='Utilisateur'
        )
        
        self.assertNotEqual(identity1.id, identity2.id)
        
    def test_get_contextual_data_legal(self):
        """Test contextual data for legal context"""
        identity = Identity.objects.create(
            user=self.user,
            context='legal',
            given_name='John',
            family_name='Doe',
            middle_name='William',
            title='Dr.',
            suffix='PhD'
        )
        
        data = identity.get_contextual_data()
        
        self.assertEqual(data['context'], 'legal')
        self.assertEqual(data['given_name'], 'John')
        self.assertEqual(data['family_name'], 'Doe')
        self.assertEqual(data['middle_name'], 'William')
        self.assertEqual(data['title'], 'Dr.')
        self.assertEqual(data['suffix'], 'PhD')
        
    def test_get_contextual_data_social(self):
        """Test contextual data for social context"""
        identity = Identity.objects.create(
            user=self.user,
            context='social',
            given_name='John',
            family_name='Doe',
            preferred_name='Johnny',
            nickname='JD',
            pronouns='he/him',
            bio='Software developer'
        )
        
        data = identity.get_contextual_data()
        
        self.assertEqual(data['context'], 'social')
        self.assertEqual(data['preferred_name'], 'Johnny')
        self.assertEqual(data['nickname'], 'JD')
        self.assertEqual(data['pronouns'], 'he/him')
        self.assertEqual(data['bio'], 'Software developer')
        
    def test_custom_attributes(self):
        """Test custom attributes JSON field"""
        custom_data = {
            'employee_id': '12345',
            'department': 'Engineering',
            'clearance_level': 'Secret'
        }
        
        identity = Identity.objects.create(
            user=self.user,
            context='professional',
            given_name='John',
            family_name='Doe',
            custom_attributes=custom_data
        )
        
        data = identity.get_contextual_data()
        self.assertEqual(data['custom_attributes'], custom_data)

class FieldPermissionTestCase(TestCase):
    """Test cases for FieldPermission model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com'
        )
        
        self.identity = Identity.objects.create(
            user=self.user,
            context='professional',
            given_name='Test',
            family_name='User'
        )
        
    def test_field_permission_creation(self):
        """Test creating field permissions"""
        permission = FieldPermission.objects.create(
            identity=self.identity,
            field_name='email',
            permission_level='read'
        )
        
        self.assertEqual(permission.identity, self.identity)
        self.assertEqual(permission.field_name, 'email')
        self.assertEqual(permission.permission_level, 'read')
        
    def test_allowed_users_many_to_many(self):
        """Test allowed users many-to-many relationship"""
        permission = FieldPermission.objects.create(
            identity=self.identity,
            field_name='phone',
            permission_level='read'
        )
        
        permission.allowed_users.add(self.other_user)
        
        self.assertIn(self.other_user, permission.allowed_users.all())

class UserRoleTestCase(TestCase):
    """Test cases for UserRole model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        
    def test_user_role_creation(self):
        """Test creating user roles"""
        # UserRole is automatically created by signals, so get the existing one
        role = UserRole.objects.get(user=self.user)

        # Update it with test values
        role.role = 'admin'
        role.organization = 'Test Corp'
        role.can_manage_users = True
        role.save()

        self.assertEqual(role.user, self.user)
        self.assertEqual(role.role, 'admin')
        self.assertTrue(role.can_manage_users)
        self.assertTrue(role.is_admin)
        
    def test_superuser_is_admin(self):
        """Test that superuser is considered admin"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )

        # UserRole is automatically created by signals for superusers with 'admin' role
        role = UserRole.objects.get(user=superuser)

        # Test that even if we change role to 'user', it's still admin due to superuser status
        role.role = 'user'
        role.save()

        self.assertTrue(role.is_admin)
        
    def test_can_access_admin_panel(self):
        """Test admin panel access permissions"""
        # Create a different user for this test since UserRole is OneToOneField
        manager_user = User.objects.create_user(username='manager')

        # UserRole is automatically created by signals, so get the existing one
        role = UserRole.objects.get(user=manager_user)

        # Update it with test values
        role.role = 'manager'
        role.can_manage_users = True
        role.save()

        self.assertTrue(role.can_access_admin_panel)

class OAuth2IntegrationTestCase(TestCase):
    """Test cases for OAuth2 integration"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.identity = Identity.objects.create(
            user=self.user,
            context='display',
            given_name='Test',
            family_name='User',
            email='test@example.com',
            is_primary=True
        )
        
        self.application = Application.objects.create(
            name="ContextID Client",
            client_id="contextid-client",
            client_secret="contextid-secret-key",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="http://localhost/callback/",
        )
        
        self.client = Client()
        
    def test_authorization_view_requires_login(self):
        """Test that authorization view requires authentication"""
        url = reverse('oauth2_authorize')
        response = self.client.get(url + '?client_id=contextid-client&response_type=code')
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
    def test_authorization_view_with_authenticated_user(self):
        """Test authorization view with authenticated user"""
        self.client.login(username='testuser', password='testpass')

        url = reverse('oauth2_authorize')
        params = {
            'client_id': 'contextid-client',
            'response_type': 'code',
            'redirect_uri': 'http://localhost/callback/',
            'scope': 'read'
        }
        response = self.client.get(url, params)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login with ContextID')
        self.assertContains(response, 'Choose which identity context to share')
        
    def test_authorization_creates_identity_if_none_exists(self):
        """Test that authorization view creates identity if user has none"""
        # Delete the existing identity
        Identity.objects.filter(user=self.user).delete()

        self.client.login(username='testuser', password='testpass')

        url = reverse('oauth2_authorize')
        params = {
            'client_id': 'contextid-client',
            'response_type': 'code',
            'redirect_uri': 'http://localhost/callback/',
            'scope': 'read'
        }
        response = self.client.get(url, params)

        self.assertEqual(response.status_code, 200)

        # Should have created a basic identity
        identity = Identity.objects.filter(user=self.user).first()
        self.assertIsNotNone(identity)
        self.assertEqual(identity.context, 'display')
        self.assertTrue(identity.is_primary)
        
    def test_oauth_user_info_endpoint(self):
        """Test the OAuth user info endpoint"""
        self.client.login(username='testuser', password='testpass')
        
        # Set selected context in session
        session = self.client.session
        session['oauth_selected_context'] = 'display'
        session.save()
        
        url = reverse('oauth_user_info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['context'], 'display')
        self.assertEqual(data['full_name'], 'Test User')
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['context_used'], 'display')


class APIEndpointTestCase(TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        self.identity = Identity.objects.create(
            user=self.user,
            context='professional',
            given_name='John',
            family_name='Doe',
            email='john.doe@company.com',
            title='Software Engineer'
        )
        
        self.client = Client()
        
    def test_identity_list_requires_authentication(self):
        """Test that identity list endpoint requires authentication"""
        url = reverse('identity-list-create')
        response = self.client.get(url)
        
        # Should return 401 or redirect to login
        self.assertIn(response.status_code, [401, 302])
        
    def test_identity_list_authenticated(self):
        """Test identity list with authenticated user"""
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('identity-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
    def test_contextual_identity_view(self):
        """Test contextual identity API endpoint"""
        self.client.login(username='testuser', password='testpass')
        
        url = reverse('contextual-identity', kwargs={'user_id': self.user.id})
        response = self.client.get(url, HTTP_ACCEPT_CONTEXT='professional')
        
        self.assertEqual(response.status_code, 200)


class IntegrationTestCase(TestCase):
    """Integration tests for the complete OAuth2 flow"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        
        # Create multiple identity contexts
        self.legal_identity = Identity.objects.create(
            user=self.user,
            context='legal',
            given_name='John',
            family_name='Doe',
            middle_name='William',
            title='Dr.',
            suffix='PhD'
        )
        
        self.social_identity = Identity.objects.create(
            user=self.user,
            context='social',
            given_name='John',
            family_name='Doe',
            preferred_name='Johnny',
            pronouns='he/him',
            bio='Love coding and coffee'
        )
        
        self.professional_identity = Identity.objects.create(
            user=self.user,
            context='professional',
            given_name='John',
            family_name='Doe',
            title='Senior Developer',
            email='john.doe@company.com',
            is_primary=True
        )
        
        self.application = Application.objects.create(
            name="ContextID Client",
            client_id="contextid-client",
            client_secret="contextid-secret-key",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris="http://localhost/callback/",
        )
        
        self.client = Client()
        
    def test_full_oauth_flow_with_context_selection(self):
        """Test the complete OAuth flow with context selection"""
        # 1. Start OAuth flow
        self.client.login(username='testuser', password='testpass')

        auth_url = reverse('oauth2_authorize')
        params = {
            'client_id': 'contextid-client',
            'response_type': 'code',
            'redirect_uri': 'http://localhost/callback/',
            'scope': 'read'
        }

        response = self.client.get(auth_url, params)
        self.assertEqual(response.status_code, 200)
        
        # 2. Should show context selection
        self.assertContains(response, 'Choose which identity context to share')
        self.assertContains(response, 'Legal')
        self.assertContains(response, 'Social') 
        self.assertContains(response, 'Professional')
        
        # 3. Select professional context and authorize
        post_data = {
            'selected_context': 'professional',
            'allow': 'allow'
        }
        post_data.update(params)
        
        response = self.client.post(auth_url, post_data)
        
        # Should redirect to callback URL with authorization code
        self.assertEqual(response.status_code, 302)
        self.assertIn('code=', response.url)
        
    def test_integration_test_page(self):
        """Test the integration test page"""
        url = reverse('oauth_integration_test')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login with ContextID')
        self.assertContains(response, 'Sample Client Application')
        
    def test_callback_page(self):
        """Test the OAuth callback page"""
        url = reverse('oauth_callback')
        response = self.client.get(url + '?code=test_code&state=test_state')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Authentication Successful')


class AdminFunctionalityTestCase(TestCase):
    """Test cases for admin functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user'
        )
        
        self.identity = Identity.objects.create(
            user=self.regular_user,
            context='display',
            given_name='Test',
            family_name='User',
            is_verified=False
        )
        
        self.client = Client()
        
    def test_admin_dashboard_access(self):
        """Test admin dashboard access"""
        # Regular user should not access admin dashboard
        self.client.login(username='user', password='user')
        response = self.client.get(reverse('admin-dashboard'))
        self.assertIn(response.status_code, [302, 403])
        
        # Admin user should access admin dashboard  
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 200)
        
    def test_user_management_access(self):
        """Test user management access"""
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('user-management'))
        self.assertEqual(response.status_code, 200)
        
    def test_identity_verification(self):
        """Test identity verification functionality"""
        self.client.login(username='admin', password='admin')
        
        url = reverse('verify-identity', kwargs={'identity_id': self.identity.id})
        response = self.client.post(url)
        
        # Should redirect after verification
        self.assertEqual(response.status_code, 302)
        
        # Check that identity is now verified
        self.identity.refresh_from_db()
        self.assertTrue(self.identity.is_verified)
        self.assertEqual(self.identity.verified_by, self.admin_user)


class SecurityTestCase(TestCase):
    """Test cases for security features"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass1'
        )
        
        self.user2 = User.objects.create_user(
            username='user2', 
            password='pass2'
        )
        
        self.identity1 = Identity.objects.create(
            user=self.user1,
            context='private',
            given_name='Private',
            family_name='User',
            visibility='private'
        )
        
        self.client = Client()
        
    def test_user_cannot_access_other_user_identities(self):
        """Test that users cannot access other users' private identities"""
        self.client.login(username='user2', password='pass2')
        
        url = reverse('identity-detail', kwargs={'pk': self.identity1.id})
        response = self.client.get(url)
        
        # Should not be able to access
        self.assertIn(response.status_code, [403, 404])
        
    def test_access_logging(self):
        """Test that identity access is logged"""
        self.client.login(username='user1', password='pass1')
        
        # Access own identity
        url = reverse('identity-detail', kwargs={'pk': self.identity1.id})
        response = self.client.get(url)
        
        # Check if access was logged (implementation depends on your logging setup)
        # This is a placeholder - you may need to adjust based on actual logging implementation
        pass


if __name__ == '__main__':
    import django
    django.setup()
    
    # Run specific test cases
    import unittest
    unittest.main()