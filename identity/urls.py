from django.urls import path, include
from . import views

# API URLs
api_urlpatterns = [
    path('identities/', views.IdentityListCreateView.as_view(), name='identity-list-create'),
    path('identities/<int:pk>/', views.IdentityDetailView.as_view(), name='identity-detail'),
    path('users/<int:user_id>/identity/', views.ContextualIdentityView.as_view(), name='contextual-identity'),
    path('users/<int:user_id>/identities/', views.UserIdentitiesView.as_view(), name='user-identities'),
    path('identities/<int:identity_id>/set-primary/', views.set_primary_identity, name='set-primary'),
    path('context-priorities/', views.ContextPriorityView.as_view(), name='context-priorities'),
]

# Web UI URLs
web_urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('identity/new/', views.identity_form, name='identity-create'),
    path('identity/<int:identity_id>/edit/', views.identity_form, name='identity-edit'),
    path('identity/<int:identity_id>/permissions/', views.permissions_panel, name='permissions'),

    # AJAX endpoints
    path('ajax/identity/update/', views.update_identity_ajax, name='ajax-identity-update'),
    path('ajax/identity/<int:identity_id>/data/', views.get_identity_data, name='ajax-identity-data'),
    path('ajax/identity/<int:identity_id>/delete/', views.delete_identity_ajax, name='ajax-identity-delete'),
    path('ajax/permission/update/', views.update_field_permission_ajax, name='ajax-permission-update'),
]

# Admin URLs
# Add to admin_urlpatterns in identity_app/urls.py

admin_urlpatterns = [
    path('admin-panel/', views.admin_dashboard, name='admin-dashboard'),
    path('admin-panel/users/', views.user_management, name='user-management'),
    path('admin-panel/users/create/', views.create_user_ajax, name='create-user-ajax'),
    path('admin-panel/users/<int:user_id>/toggle-status/', views.toggle_user_status_ajax, name='toggle-user-status'),
    path('admin-panel/identities/', views.identity_management, name='identity-management'),
    path('admin-panel/identities/<int:identity_id>/details/', views.identity_details_ajax, name='identity-details-ajax'),
    path('admin-panel/users/<int:user_id>/', views.user_detail_admin, name='user-detail-admin'),
    path('admin-panel/verify/<int:identity_id>/', views.verify_identity, name='verify-identity'),
]

urlpatterns = [
                  path('api/v1/', include(api_urlpatterns)),
              ] + web_urlpatterns + admin_urlpatterns
