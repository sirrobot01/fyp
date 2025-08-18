from identity.models import UserRole
from identity.views.utils import is_admin_user


def global_context(request):
    """
    Context processor to add common variables to all templates.
    This can include site name, user info, etc.
    """
    return {
        'site_name': 'Identity Management System',
        'is_admin': is_admin_user(request.user) if request.user.is_authenticated else False,
    }
