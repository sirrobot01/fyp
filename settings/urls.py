"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# identity_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from identity.oauth_views import CustomAuthorizationView, oauth_login_demo, oauth_callback_demo, oauth_user_info

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom OAuth2 authorization view (must come before oauth2_provider URLs)
    path('o/authorize/', CustomAuthorizationView.as_view(), name='oauth2_authorize'),
    
    # Include OAuth2 provider URLs
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    
    # OAuth integration testing endpoints
    path('integration-test/', oauth_login_demo, name='oauth_integration_test'),
    path('oauth/callback/', oauth_callback_demo, name='oauth_callback'),
    path('oauth/user/', oauth_user_info, name='oauth_user_info'),
    
    path('api/v1/', include('identity.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('identity.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)