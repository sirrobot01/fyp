from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Identity, FieldPermission, ContextPriority


class IdentitySerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Identity
        fields = [
            'id', 'context', 'locale', 'given_name', 'family_name',
            'middle_name', 'preferred_name', 'display_name', 'pronouns',
            'title', 'suffix', 'nickname', 'avatar_url', 'bio', 'website',
            'email', 'phone', 'custom_attributes', 'visibility',
            'is_primary', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']

    def validate(self, data):
        """Custom validation for identity data"""
        user = self.context['request'].user
        context = data.get('context')
        locale = data.get('locale', 'en-US')

        # Check for duplicate context/locale combination
        if self.instance is None:  # Creating new instance
            if Identity.objects.filter(user=user, context=context, locale=locale).exists():
                raise serializers.ValidationError(
                    f"Identity with context '{context}' and locale '{locale}' already exists."
                )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContextualIdentitySerializer(serializers.ModelSerializer):
    """Serializer that returns only contextually appropriate fields"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Identity
        fields = ['id', 'context', 'full_name', 'visibility']

    def to_representation(self, instance):
        """Override to return contextual data"""
        request = self.context.get('request')
        requesting_user = request.user if request else None

        return instance.get_contextual_data(requesting_user)


class FieldPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldPermission
        fields = [
            'id', 'identity', 'field_name', 'permission_level',
            'allowed_roles', 'conditions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContextPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextPriority
        fields = ['id', 'context', 'priority']
        read_only_fields = ['id']

    def validate(self, data):
        """Ensure user is set from request context"""
        data['user'] = self.context['request'].user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with all identities"""
    identities = IdentitySerializer(many=True, read_only=True)
    primary_identity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'identities', 'primary_identity', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']

    def get_primary_identity(self, obj):
        """Get the primary identity for the user"""
        primary = obj.identities.filter(is_primary=True).first()
        return IdentitySerializer(primary).data if primary else None
