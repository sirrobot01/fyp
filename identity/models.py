from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import json


class Identity(models.Model):
    CONTEXT_CHOICES = [
        ('legal', 'Legal'),
        ('display', 'Display'),
        ('social', 'Social'),
        ('professional', 'Professional'),
        ('username', 'Username'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private'),
        ('organization', 'Organization Only'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identities')
    context = models.CharField(max_length=20, choices=CONTEXT_CHOICES)
    locale = models.CharField(
        max_length=10,
        default='en-US',
        validators=[RegexValidator(r'^[a-z]{2}-[A-Z]{2}$', 'Invalid locale format')]
    )

    # Core name fields
    given_name = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    preferred_name = models.CharField(max_length=100, blank=True)
    display_name = models.CharField(max_length=200, blank=True)

    # Extended attributes
    pronouns = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=50, blank=True)
    suffix = models.CharField(max_length=20, blank=True)
    nickname = models.CharField(max_length=50, blank=True)

    # Social and professional
    avatar_url = models.URLField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)

    # Contact information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Custom attributes (JSON field for extensibility)
    custom_attributes = models.JSONField(default=dict, blank=True)

    # Privacy and permissions
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin-only fields
    admin_notes = models.TextField(blank=True, help_text="Admin-only notes")
    is_verified = models.BooleanField(default=False, help_text="Admin verified identity")
    verification_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_identities'
    )

    class Meta:
        unique_together = ['user', 'context', 'locale']
        ordering = ['-is_primary', 'context', 'created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.context})"

    def get_full_name(self):
        """Return the full name based on context preferences"""
        if self.display_name:
            return self.display_name

        parts = []
        if self.title:
            parts.append(self.title)

        if self.preferred_name and self.context in ['social', 'display']:
            parts.append(self.preferred_name)
        else:
            parts.append(self.given_name)

        if self.middle_name and self.context == 'legal':
            parts.append(self.middle_name)

        parts.append(self.family_name)

        if self.suffix:
            parts.append(self.suffix)

        return ' '.join(parts)

    def get_contextual_data(self, requesting_user=None, requested_fields=None):
        """Return data appropriate for the context and requesting user"""
        data = {
            'id': self.id,
            'context': self.context,
            'locale': self.locale,
            'full_name': self.get_full_name(),
            'visibility': self.visibility,
        }

        # Determine what fields to include based on context
        if self.context == 'legal':
            data.update({
                'given_name': self.given_name,
                'family_name': self.family_name,
                'middle_name': self.middle_name,
                'title': self.title,
                'suffix': self.suffix,
            })
        elif self.context == 'social':
            data.update({
                'preferred_name': self.preferred_name or self.given_name,
                'nickname': self.nickname,
                'pronouns': self.pronouns,
                'avatar_url': self.avatar_url,
                'bio': self.bio,
            })
        elif self.context == 'professional':
            data.update({
                'given_name': self.given_name,
                'family_name': self.family_name,
                'title': self.title,
                'email': self.email,
                'website': self.website,
                'bio': self.bio,
            })
        elif self.context == 'display':
            data.update({
                'display_name': self.display_name or self.get_full_name(),
                'pronouns': self.pronouns,
                'avatar_url': self.avatar_url,
            })

        # Add custom attributes if they exist
        if self.custom_attributes:
            data['custom_attributes'] = self.custom_attributes

        return data


class FieldPermission(models.Model):
    PERMISSION_LEVELS = [
        ('none', 'No Access'),
        ('read', 'Read Only'),
        ('write', 'Read & Write'),
        ('admin', 'Full Control'),
    ]

    identity = models.ForeignKey(Identity, on_delete=models.CASCADE, related_name='field_permissions')
    field_name = models.CharField(max_length=50)
    permission_level = models.CharField(max_length=10, choices=PERMISSION_LEVELS, default='read')

    # Role-based permissions
    allowed_roles = models.JSONField(default=list, blank=True)
    allowed_users = models.ManyToManyField(User, blank=True)

    # Conditional permissions
    conditions = models.JSONField(default=dict, blank=True)  # For future extensibility

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['identity', 'field_name']

    def __str__(self):
        return f"{self.identity} - {self.field_name}: {self.permission_level}"


class ContextPriority(models.Model):
    """Defines priority order for context resolution"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='context_priorities')
    context = models.CharField(max_length=20)
    priority = models.IntegerField(default=0)  # Lower number = higher priority

    class Meta:
        unique_together = ['user', 'context']
        ordering = ['priority']


class AccessLog(models.Model):
    """Audit trail for identity access"""
    identity = models.ForeignKey(Identity, on_delete=models.CASCADE, related_name='access_logs')
    accessed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    accessed_fields = models.JSONField(default=list)
    access_context = models.CharField(max_length=20)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.accessed_by} accessed {self.identity} at {self.timestamp}"

class UserRole(models.Model):
    """Extended user profile with roles"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('user', 'Standard User'),
        ('manager', 'Manager'),
        ('viewer', 'Viewer Only'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_organization_admin = models.BooleanField(default=False)
    organization = models.CharField(max_length=100, blank=True)
    can_manage_users = models.BooleanField(default=False)
    can_view_all_identities = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def can_access_admin_panel(self):
        return self.is_admin or self.can_manage_users
