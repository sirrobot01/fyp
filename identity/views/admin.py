import json

from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from .utils import is_admin_user
from ..models import UserRole, Identity
from django.utils import timezone


@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """Admin-only dashboard"""
    # Get statistics
    total_users = User.objects.count()
    total_identities = Identity.objects.count()
    unverified_identities = Identity.objects.filter(is_verified=False).count()

    # Recent activity
    recent_identities = Identity.objects.select_related('user').order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:10]

    context = {
        'total_users': total_users,
        'total_identities': total_identities,
        'unverified_identities': unverified_identities,
        'recent_identities': recent_identities,
        'recent_users': recent_users,
    }
    return render(request, 'admin_dashboard.html', context)


@user_passes_test(is_admin_user)
def user_management(request):
    """User management page for admins"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')

    users = User.objects.select_related('profile').order_by('-date_joined')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if role_filter:
        users = users.filter(profile__role=role_filter)

    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_choices': UserRole.ROLE_CHOICES,
    }
    return render(request, 'user_management.html', context)


@user_passes_test(is_admin_user)
def identity_management(request):
    """Identity management page for admins"""
    search_query = request.GET.get('search', '')
    context_filter = request.GET.get('context', '')
    verification_filter = request.GET.get('verified', '')

    identities = Identity.objects.select_related('user').order_by('-created_at')

    if search_query:
        identities = identities.filter(
            Q(given_name__icontains=search_query) |
            Q(family_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    if context_filter:
        identities = identities.filter(context=context_filter)

    if verification_filter == 'verified':
        identities = identities.filter(is_verified=True)
    elif verification_filter == 'unverified':
        identities = identities.filter(is_verified=False)

    paginator = Paginator(identities, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'context_filter': context_filter,
        'verification_filter': verification_filter,
        'context_choices': Identity.CONTEXT_CHOICES,
    }
    return render(request, 'identity_management.html', context)


@user_passes_test(is_admin_user)
def verify_identity(request, identity_id):
    """Verify an identity (admin only)"""
    identity = get_object_or_404(Identity, id=identity_id)

    if request.method == 'POST':
        identity.is_verified = True
        identity.verification_date = timezone.now()
        identity.verified_by = request.user
        identity.admin_notes = request.POST.get('admin_notes', '')
        identity.save()

        messages.success(request, f'Identity for {identity.get_full_name()} has been verified.')
        return redirect('identity-management')

    return render(request, 'verify_identity.html', {'identity': identity})


@user_passes_test(is_admin_user)
def user_detail_admin(request, user_id):
    """Admin view of user details"""
    user = get_object_or_404(User, id=user_id)
    user_identities = Identity.objects.filter(user=user)

    context = {
        'viewed_user': user,
        'user_identities': user_identities,
        'total_identities': user_identities.count(),
        'verified_identities': user_identities.filter(is_verified=True).count(),
    }
    return render(request, 'user_detail_admin.html', context)


@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def create_user_ajax(request):
    """Create new user via AJAX"""
    try:
        data = json.loads(request.body)

        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )

        # Update profile role
        if hasattr(user, 'profile'):
            user.profile.role = data.get('role', 'user')
            user.profile.save()

        return JsonResponse({
            'success': True,
            'user_id': user.id,
            'message': f'User {user.username} created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
def toggle_user_status_ajax(request, user_id):
    """Toggle user active status"""
    try:
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)

        user.is_active = data.get('is_active', not user.is_active)
        user.save()

        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'User {user.username} {"activated" if user.is_active else "deactivated"}'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@user_passes_test(is_admin_user)
def identity_details_ajax(request, identity_id):
    """Get identity details for modal"""
    try:
        identity = get_object_or_404(Identity, id=identity_id)

        data = {
            'success': True,
            'identity': {
                'id': identity.id,
                'full_name': identity.get_full_name(),
                'context': identity.get_context_display(),
                'locale': identity.locale,
                'visibility': identity.get_visibility_display(),
                'email': identity.email,
                'phone': identity.phone,
                'website': identity.website,
                'pronouns': identity.pronouns,
                'bio': identity.bio,
                'custom_attributes': identity.custom_attributes,
                'is_verified': identity.is_verified,
                'verified_by': identity.verified_by.username if identity.verified_by else None,
                'admin_notes': identity.admin_notes,
                'created_at': identity.created_at.isoformat(),
                'updated_at': identity.updated_at.isoformat(),
            }
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })