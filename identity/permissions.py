from rest_framework import permissions
from oauth2_provider.models import AccessToken
from .models import FieldPermission


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner
        return obj.user == request.user


class FieldLevelPermission(permissions.BasePermission):
    """
    Permission class that enforces field-level access control
    """

    def has_permission(self, request, view):
        # Basic authentication check
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if user can access this identity at all
        if obj.user == request.user:
            return True

        # Check field-level permissions
        if hasattr(obj, 'field_permissions'):
            # This would be implemented based on specific field access
            return self.check_field_permissions(request, obj)

        # Default to visibility-based access
        return self.check_visibility_access(request, obj)

    def check_field_permissions(self, request, obj):
        """Check specific field permissions"""
        # Implementation for field-level permission checking
        # This is a simplified version
        return True

    def check_visibility_access(self, request, obj):
        """Check access based on visibility settings"""
        if obj.visibility == 'public':
            return True
        elif obj.visibility == 'private':
            return obj.user == request.user
        elif obj.visibility == 'friends':
            # This would check if users are friends/connected
            return False  # Simplified for now

        return False


class ContextBasedPermission(permissions.BasePermission):
    """
    Permission that varies based on the requested context
    """

    def has_permission(self, request, view):
        # Extract context from headers
        context = request.META.get('HTTP_ACCEPT_CONTEXT', 'display')

        # Different contexts might have different permission requirements
        # if context == 'legal':
        #     # Legal context might require higher permissions
        #     return request.user.is_authenticated and hasattr(request.user, 'legal_access')

        return request.user.is_authenticated


class OAuth2ScopePermission(permissions.BasePermission):
    """
    Permission class that checks OAuth2 scopes
    """
    required_scopes = []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check if this is an OAuth2 request
        if hasattr(request, 'auth') and isinstance(request.auth, AccessToken):
            token = request.auth
            token_scopes = token.scope.split()

            # Check if required scopes are present
            return all(scope in token_scopes for scope in self.required_scopes)

        # If not OAuth2, fall back to regular authentication
        return True


class ReadScopePermission(OAuth2ScopePermission):
    required_scopes = ['read']


class WriteScopePermission(OAuth2ScopePermission):
    required_scopes = ['write']


class AdminScopePermission(OAuth2ScopePermission):
    required_scopes = ['admin']
