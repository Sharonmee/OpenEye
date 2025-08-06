from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    """Main scanner view - requires login"""
    if request.user.is_authenticated:
        cognito_user_info = request.session.get('cognito_user_info', {})
        user_email = cognito_user_info.get('email', request.user.email)
        return render(request, 'home.html', {
            'user_email': user_email,
            'cognito_user_info': cognito_user_info
        })
    else:
        return HttpResponse("Please log in to access the scanner. <a href='/login/'>Login with Cognito</a>")

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        cognito_user_info = request.session.get('cognito_user_info', {})
        user_email = cognito_user_info.get('email', request.user.email)
        return render(request, 'home.html', {
            'user': request.user,
            'user_email': user_email,
            'cognito_user_info': cognito_user_info
        })
    else:
        return render(request, 'home.html')

@login_required
def scan(request):
    """Scan page view - requires authentication"""
    cognito_user_info = request.session.get('cognito_user_info', {})
    user_email = cognito_user_info.get('email', request.user.email)
    return render(request, 'scanner/scan.html', {
        'user': request.user,
        'user_email': user_email,
        'cognito_user_info': cognito_user_info
    })