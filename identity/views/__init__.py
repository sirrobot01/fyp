from .api import (
    IdentityListCreateView,
    IdentityDetailView,
    ContextualIdentityView,
    UserIdentitiesView,
    set_primary_identity,
    ContextPriorityView,
)
from .web import (
    home,
    dashboard,
    identity_form,
    permissions_panel,
)
from .ajax import (
    update_identity_ajax,
    get_identity_data,
    delete_identity_ajax,
    update_field_permission_ajax,
)

from .admin import (
    admin_dashboard,
    user_management,
    user_detail_admin,
    identity_management,
    verify_identity,
    identity_details_ajax,
    create_user_ajax,
    toggle_user_status_ajax,
)
