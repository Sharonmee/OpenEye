import requests
import base64
import json
import secrets
from urllib.parse import urlencode
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.models import User
from django.contrib import messages
from OpenEye.oauth import (
    COGNITO_CLIENT_ID, 
    COGNITO_CLIENT_SECRET,
    AUTHORIZATION_ENDPOINT,
    TOKEN_ENDPOINT,
    USERINFO_ENDPOINT,
    SCOPES,
    COGNITO_DOMAIN
)

def cognito_login(request):
    """Redirect user to Cognito login page"""
    redirect_uri = request.build_absolute_uri(reverse('cognito_callback'))
    redirect_uri = redirect_uri.replace('127.0.0.1', 'localhost')
    
    # Generate a random state parameter for security
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Build authorization URL manually
    params = {
        'response_type': 'code',
        'client_id': COGNITO_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(SCOPES),
        'state': state
    }
    
    authorization_url = f"{AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
    
    # # Debug information - let's see what's actually being generated
    # print("=" * 50)
    # print("COGNITO LOGIN DEBUG:")
    # print(f"Redirect URI: {redirect_uri}")
    # print(f"Authorization URL: {authorization_url}")
    # print(f"Authorization Endpoint: {AUTHORIZATION_ENDPOINT}")
    # print(f"Cognito Domain: {COGNITO_DOMAIN}")
    # print("=" * 50)
    
    return HttpResponseRedirect(authorization_url)

def cognito_callback(request):
    """Handle callback from Cognito after authentication"""
    # Get the authorization code from the callback
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    # Verify state parameter
    if state != request.session.get('oauth_state'):
        messages.error(request, 'Invalid state parameter')
        return redirect('home')
    
    if not code:
        messages.error(request, 'Authorization code not received')
        return redirect('home')
    
    try:
        # Exchange authorization code for access token
        redirect_uri = request.build_absolute_uri(reverse('cognito_callback'))
        
        # Prepare token request
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': COGNITO_CLIENT_ID,
            'client_secret': COGNITO_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        # Request access token
        token_response = requests.post(TOKEN_ENDPOINT, data=token_data)
        token_response.raise_for_status()
        token = token_response.json()
        
        # Get user info using access token
        headers = {'Authorization': f"Bearer {token['access_token']}"}
        user_response = requests.get(USERINFO_ENDPOINT, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Create or get Django user
        email = user_info.get('email')
        username = user_info.get('username', email)
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
            }
        )
        
        # Store Cognito user info in session
        request.session['cognito_user_info'] = user_info
        request.session['cognito_access_token'] = token.get('access_token')
        
        # Log in the user
        django_login(request, user)
        
        messages.success(request, f'Successfully logged in as {email}')
        return redirect('scanner:index')  # Redirect to your scanner app
        
    except Exception as e:
        messages.error(request, f'Authentication failed: {str(e)}')
        return redirect('home')

def cognito_logout(request):
    """Log out user and clear session"""
    # Clear Cognito session data
    request.session.pop('cognito_user_info', None)
    request.session.pop('cognito_access_token', None)
    request.session.pop('oauth_state', None)
    
    # Django logout
    django_logout(request)
    
    messages.success(request, 'Successfully logged out')
    return redirect('home')
