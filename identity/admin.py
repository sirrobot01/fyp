from django.contrib import admin
from django.utils.html import format_html
from .models import Identity, FieldPermission, ContextPriority, AccessLog


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user', 'context', 'locale', 'visibility', 'is_primary', 'is_active', 'created_at']
    list_filter = ['context', 'visibility', 'is_primary', 'is_active', 'created_at']
    search_fields = ['given_name', 'family_name', 'preferred_name', 'email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'context', 'locale', 'is_primary', 'is_active')
        }),
        ('Name Details', {
            'fields': (
            'given_name', 'family_name', 'middle_name', 'preferred_name', 'display_name', 'title', 'suffix', 'nickname')
        }),
        ('Personal Information', {
            'fields': ('pronouns', 'email', 'phone', 'avatar_url', 'bio', 'website')
        }),
        ('Privacy Settings', {
            'fields': ('visibility', 'custom_attributes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'given_name'


@admin.register(FieldPermission)
class FieldPermissionAdmin(admin.ModelAdmin):
    list_display = ['identity', 'field_name', 'permission_level', 'created_at']
    list_filter = ['permission_level', 'field_name', 'created_at']
    search_fields = ['identity__given_name', 'identity__family_name', 'field_name']


@admin.register(ContextPriority)
class ContextPriorityAdmin(admin.ModelAdmin):
    list_display = ['user', 'context', 'priority']
    list_filter = ['context']
    search_fields = ['user__username']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['identity', 'accessed_by', 'access_context', 'timestamp', 'ip_address']
    list_filter = ['access_context', 'timestamp']
    search_fields = ['identity__given_name', 'accessed_by__username', 'ip_address']
    readonly_fields = ['timestamp']

    def has_add_permission(self, request):
        return False  # Don't allow manual creation of access logs

    def has_change_permission(self, request, obj=None):
        return False  # Don't allow editing of access logs
