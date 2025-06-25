from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from oauth2_provider.views import AuthorizationView
from oauth2_provider.models import get_application_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from collections import defaultdict
from .models import Identity

Application = get_application_model()


@method_decorator([csrf_protect, never_cache], name="dispatch")
class CustomAuthorizationView(AuthorizationView):
    """
    Custom OAuth2 authorization view that includes user identity context selection
    """
    template_name = 'oauth2_provider/authorize.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Get user's identities grouped by context
            identities = Identity.objects.filter(
                user=self.request.user,
                is_active=True
            ).order_by('-is_primary', 'context', 'created_at')
            user_identities = defaultdict(list)
            for identity in identities:
                user_identities[identity.context].append(identity)
            
            context['user_identities'] = dict(user_identities)
            
            # If no identities exist, create a basic one for demo
            if not identities.exists():
                # Create a basic display identity for the user
                identity = Identity.objects.create(
                    user=self.request.user,
                    context='display',
                    given_name=self.request.user.first_name or self.request.user.username,
                    family_name=self.request.user.last_name or 'User',
                    email=self.request.user.email,
                    is_primary=True,
                    is_active=True
                )
                
                user_identities = {'display': [identity]}
                context['user_identities'] = user_identities
        
        return context
    
    def form_valid(self, form):
        """
        Handle form submission with selected context
        """
        print("DEBUG: Form is valid, processing OAuth authorization")
        print(f"DEBUG: POST data: {dict(self.request.POST)}")
        
        # Check if user clicked "allow" button
        if 'allow' not in self.request.POST:
            print("DEBUG: User clicked Cancel or allow button not found")
            return self.form_invalid(form)
        
        selected_context = self.request.POST.get('selected_context', 'display')
        print(f"DEBUG: Selected context: {selected_context}")
        
        # Store selected context in session for the token endpoint
        self.request.session['oauth_selected_context'] = selected_context
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Handle invalid form or user denial
        """
        print("DEBUG: Form invalid or user denied access")
        print(f"DEBUG: Form errors: {form.errors}")
        return super().form_invalid(form)


def oauth_login_demo(request):
    """
    Demo page showing how to integrate "Login with IMA" button
    """
    # This would be on your client application
    oauth_url = (
        f"{request.scheme}://{request.get_host()}/o/authorize/"
        f"?response_type=code"
        f"&client_id=YOUR_CLIENT_ID"
        f"&redirect_uri=YOUR_CALLBACK_URL"
        f"&scope=read"
        f"&state=random_state_string"
    )
    
    return render(request, 'oauth2_provider/login_demo.html', {
        'oauth_url': oauth_url
    })


def oauth_callback_demo(request):
    """
    Demo callback handler - this would be on your client application
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'OAuth error: {error}')
        return redirect('oauth_integration_test')
    
    if not code:
        messages.error(request, 'No authorization code received')
        return redirect('oauth_integration_test')
    
    # In a real application, you would:
    # 1. Exchange the code for an access token
    # 2. Use the access token to get user data
    # 3. Create/update user account in your system
    
    return render(request, 'oauth2_provider/callback_demo.html', {
        'code': code,
        'state': state
    })


@login_required
def oauth_user_info(request):
    """
    API endpoint that returns user info based on selected context
    This is what client applications would call after getting an access token
    """
    # Get the context that was selected during authorization
    selected_context = request.session.get('oauth_selected_context', 'display')
    
    try:
        # Get the user's identity for the selected context
        identity = Identity.objects.filter(
            user=request.user,
            context=selected_context,
            is_active=True
        ).first()
        
        if not identity:
            # Fallback to primary identity
            identity = Identity.objects.filter(
                user=request.user,
                is_primary=True,
                is_active=True
            ).first()
        
        if not identity:
            return JsonResponse({
                'error': 'No identity found'
            }, status=404)
        
        # Return contextual data
        user_data = identity.get_contextual_data(requesting_user=request.user)
        user_data.update({
            'username': request.user.username,
            'email': request.user.email,
            'context_used': selected_context,
            'is_active': request.user.is_active,
            'date_joined': request.user.date_joined.isoformat(),
        })
        
        return JsonResponse(user_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)