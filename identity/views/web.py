import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User

from .utils import group_identities_by_context
from ..models import Identity, FieldPermission, ContextPriority, AccessLog
from .utils import is_admin_user


def home(request):
    """Home page - redirect based on authentication status"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard - different views for admin vs regular users"""
    user = request.user

    # Check if user is admin
    is_admin = is_admin_user(user)

    if is_admin:
        # Admin sees overview of all users
        user_identities = Identity.objects.filter(user=request.user)
        all_identities_count = Identity.objects.count()
        all_users_count = User.objects.count()
        unverified_count = Identity.objects.filter(is_verified=False).count()
        api_calls = AccessLog.objects.all().order_by('-timestamp').count()

        context = {
            'identities': user_identities,
            'context_groups': group_identities_by_context(user_identities),
            'context_choices': Identity.CONTEXT_CHOICES,
            'total_identities': user_identities.count(),
            'is_admin': True,
            'api_calls': api_calls,
            'admin_stats': {
                'all_identities': all_identities_count,
                'all_users': all_users_count,
                'unverified': unverified_count,
            }
        }
    else:
        # Regular user sees only their own identities
        user_identities = Identity.objects.filter(user=request.user)
        api_calls = AccessLog.objects.all().order_by('-timestamp').count()
        context = {
            'identities': user_identities,
            'context_choices': Identity.CONTEXT_CHOICES,
            'context_groups': group_identities_by_context(user_identities),
            'total_identities': user_identities.count(),
            'is_admin': False,
            'api_calls': api_calls,
        }

    return render(request, 'dashboard.html', context)


@login_required
def identity_form(request, identity_id=None):
    """Form for creating/editing identities"""
    identity = None
    if identity_id:
        identity = get_object_or_404(Identity, id=identity_id, user=request.user)

    if request.method == 'POST':
        # Handle form submission
        data = request.POST.dict()

        # Handle custom attributes
        custom_attrs = {}
        for key, value in data.items():
            if key.startswith('custom_'):
                attr_name = key.replace('custom_', '')
                custom_attrs[attr_name] = value

        if custom_attrs:
            data['custom_attributes'] = json.dumps(custom_attrs)

        # Create or update identity
        if identity:
            # Update existing
            for field, value in data.items():
                if hasattr(identity, field) and field != 'csrfmiddlewaretoken':
                    setattr(identity, field, value)
            identity.save()
        else:
            # Create new
            data['user'] = request.user
            identity = Identity.objects.create(**data)

        return JsonResponse({'success': True, 'identity_id': identity.id})

    context = {
        'identity': identity,
        'context_choices': Identity.CONTEXT_CHOICES,
        'visibility_choices': Identity.VISIBILITY_CHOICES,
    }
    return render(request, 'identity_form.html', context)


@login_required
def permissions_panel(request, identity_id):
    """Permissions management panel"""
    identity = get_object_or_404(Identity, id=identity_id, user=request.user)
    field_permissions = FieldPermission.objects.filter(identity=identity)

    context = {
        'identity': identity,
        'field_permissions': field_permissions,
        'permission_levels': FieldPermission.PERMISSION_LEVELS,
        'available_fields': [
            'given_name', 'family_name', 'email', 'phone',
            'pronouns', 'avatar_url', 'bio', 'website'
        ],
    }
    return render(request, 'permissions.html', context)
