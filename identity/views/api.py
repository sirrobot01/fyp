from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Identity, ContextPriority, AccessLog
from ..permissions import (
    IsOwnerOrReadOnly, ContextBasedPermission, ReadScopePermission, WriteScopePermission
)
from ..serializers import (
    IdentitySerializer, ContextualIdentitySerializer,
    ContextPrioritySerializer
)


class IdentityListCreateView(generics.ListCreateAPIView):
    """
    List all identities for the authenticated user or create a new identity
    """
    serializer_class = IdentitySerializer
    permission_classes = [permissions.IsAuthenticated, ReadScopePermission]

    def get_queryset(self):
        return Identity.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), WriteScopePermission()]
        return [permissions.IsAuthenticated(), ReadScopePermission()]


class IdentityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an identity
    """
    serializer_class = IdentitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Identity.objects.filter(user=self.request.user)


class ContextualIdentityView(APIView):
    """
    Get identity data based on Accept-Context header
    """
    permission_classes = [permissions.IsAuthenticated, ContextBasedPermission]

    def get(self, request, user_id):
        # Parse context from header
        context = request.META.get('HTTP_ACCEPT_CONTEXT', 'display')
        locale = request.META.get('HTTP_ACCEPT_LANGUAGE', 'en-US')[:5]

        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get identity for context
        identity = Identity.objects.filter(
            user=user,
            context=context,
            locale=locale,
            is_active=True
        ).first()

        if not identity:
            # Try to find identity with same context but different locale
            identity = Identity.objects.filter(
                user=user,
                context=context,
                is_active=True
            ).first()

        if not identity:
            # Fall back to primary identity
            identity = Identity.objects.filter(
                user=user,
                is_primary=True,
                is_active=True
            ).first()

        if not identity:
            return Response({'error': 'No identity found'}, status=status.HTTP_404_NOT_FOUND)

        # Log access
        AccessLog.objects.create(
            identity=identity,
            accessed_by=request.user,
            accessed_fields=['contextual_data'],
            access_context=context,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Return contextual data
        serializer = ContextualIdentitySerializer(identity, context={'request': request})
        return Response(serializer.data)

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserIdentitiesView(APIView):
    """
    Get all identities for a specific user (with proper permissions)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if requesting user can access these identities
        if user != request.user:
            # For now, only allow access to public identities
            identities = Identity.objects.filter(
                user=user,
                visibility='public',
                is_active=True
            )
        else:
            # User accessing their own identities
            identities = Identity.objects.filter(user=user, is_active=True)

        serializer = ContextualIdentitySerializer(identities, many=True, context={'request': request})
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, WriteScopePermission])
def set_primary_identity(request, identity_id):
    """Set an identity as primary"""
    try:
        identity = Identity.objects.get(id=identity_id, user=request.user)
    except Identity.DoesNotExist:
        return Response({'error': 'Identity not found'}, status=status.HTTP_404_NOT_FOUND)

    # Remove primary from other identities
    Identity.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

    # Set this as primary
    identity.is_primary = True
    identity.save()

    return Response({'success': True, 'message': 'Primary identity updated'})


class ContextPriorityView(generics.ListCreateAPIView):
    """Manage context priorities for the user"""
    serializer_class = ContextPrioritySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ContextPriority.objects.filter(user=self.request.user)