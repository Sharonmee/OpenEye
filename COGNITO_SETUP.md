# AWS Cognito Integration with Django - Setup Complete

## What We've Implemented

1. **Converted Flask OAuth to Django**: Replaced the Flask-based OAuth with Django-compatible authentication
2. **Created Authentication Views**: 
   - `/login/` - Redirects to Cognito login
   - `/authorize/` - Handles Cognito callback
   - `/logout/` - Logs out and clears session

3. **Updated Templates**: Added login/logout buttons and user status display

4. **Configured Environment**: Set up environment variables for Cognito client secret

## AWS Cognito Configuration Required

### Step 1: Configure Domain (CRITICAL!)
In your AWS Cognito User Pool console:
1. Go to **User Pools** → `eu-west-2_eDuJb1UDY`
2. Go to **App integration** tab
3. In the **Domain** section, create a Cognito domain (e.g., `openeye-auth`)
4. Your domain will be: `openeye-auth.auth.eu-west-2.amazoncognito.com`

### Step 2: Update Environment Variables
In your `.env` file, replace:
```
COGNITO_CLIENT_SECRET=your_actual_client_secret_here
COGNITO_DOMAIN=https://your-actual-domain.auth.eu-west-2.amazoncognito.com
```

### Step 3: Configure App Client Settings
In your AWS Cognito User Pool App Client, configure:

#### Callback URLs
- `http://localhost:8000/authorize/`
- `http://127.0.0.1:8000/authorize/`

#### Sign-out URLs  
- `http://localhost:8000/`
- `http://127.0.0.1:8000/`

#### Scopes
- openid ✓
- email ✓  
- phone ✓

#### OAuth 2.0 Grant Types
- Authorization code grant ✓

#### OAuth 2.0 Flows
- Authorization code grant ✓

## How It Works

1. User clicks "Login with Cognito" on homepage
2. Redirected to AWS Cognito hosted UI
3. After authentication, Cognito redirects to `/authorize/`
4. Django exchanges auth code for access token
5. Retrieves user info from Cognito
6. Creates/updates Django user and logs them in
7. User is redirected to scanner page

## Files Modified/Created

- `OpenEye/oauth.py` - Cognito configuration
- `scanner/cognito_auth.py` - Django authentication views
- `scanner/views.py` - Updated views
- `scanner/urls.py` - Added routes
- `OpenEye/urls.py` - Main URL configuration
- `templates/home.html` - Added auth UI
- `templates/scanner/index.html` - Scanner page
- `templates/registration/login.html` - Redirect to Cognito
- `.env` - Environment variables
- `OpenEye/settings.py` - Session configuration

## Testing

1. Start server: `python manage.py runserver 8000`
2. Visit `http://localhost:8000/`
3. Click "Login with Cognito"
4. Complete authentication in Cognito
5. Should be redirected back with user logged in

**Note**: Fixed OAuth2Session issue - now using manual OAuth2 flow with requests library for better Django compatibility.

## Next Steps

1. Replace `<client secret>` in oauth.py and .env with real secret
2. Configure AWS Cognito callback URLs as listed above
3. Test the complete authentication flow
4. Add error handling and user management features as needed

## Troubleshooting

- **OAuth2Session AttributeError**: Fixed by implementing manual OAuth2 flow
- **Port already in use**: Use different port like 8001 or kill existing process
- **Invalid state parameter**: Clear browser cookies/session data
- **Callback URL mismatch**: Ensure AWS Cognito URLs match exactly
