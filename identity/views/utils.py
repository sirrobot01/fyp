from identity.models import UserRole


def is_admin_user(user):
    """Check if user has admin privileges"""
    if user.is_superuser:
        return True
    try:
        return user.profile.is_admin or user.profile.can_manage_users
    except UserRole.DoesNotExist:
        return False


def group_identities_by_context(identities):
    """Helper function to group identities by context"""
    context_groups = {}
    for identity in identities:
        context = identity.get_context_display()
        if context not in context_groups:
            context_groups[context] = []
        context_groups[context].append(identity)
    return context_groups
