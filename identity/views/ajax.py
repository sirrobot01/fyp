import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models import Identity, FieldPermission
from ..serializers import (
    IdentitySerializer
)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_identity_ajax(request):
    """AJAX endpoint for updating identity"""
    try:
        data = json.loads(request.body)
        identity_id = data.get('identity_id')

        if identity_id:
            identity = get_object_or_404(Identity, id=identity_id, user=request.user)
        else:
            identity = Identity(user=request.user)

        # Update fields
        for field, value in data.items():
            if hasattr(identity, field) and field != 'identity_id':
                setattr(identity, field, value)

        identity.save()

        return JsonResponse({
            'success': True,
            'identity_id': identity.id,
            'full_name': identity.get_full_name()
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_identity_data(request, identity_id):
    """Get identity data for editing"""
    identity = get_object_or_404(Identity, id=identity_id, user=request.user)
    serializer = IdentitySerializer(identity)
    return JsonResponse(serializer.data)


@csrf_exempt
@login_required
@require_http_methods(["DELETE"])
def delete_identity_ajax(request, identity_id):
    """Delete an identity via AJAX"""
    try:
        identity = get_object_or_404(Identity, id=identity_id, user=request.user)
        identity.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_field_permission_ajax(request):
    """Update field permissions via AJAX"""
    try:
        data = json.loads(request.body)
        identity_id = data.get('identity_id')
        field_name = data.get('field_name')
        permission_level = data.get('permission_level')

        identity = get_object_or_404(Identity, id=identity_id, user=request.user)

        # Update or create field permission
        field_permission, created = FieldPermission.objects.get_or_create(
            identity=identity,
            field_name=field_name,
            defaults={'permission_level': permission_level}
        )

        if not created:
            field_permission.permission_level = permission_level
            field_permission.save()

        return JsonResponse({
            'success': True,
            'created': created,
            'permission_id': field_permission.id
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
