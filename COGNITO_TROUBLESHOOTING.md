# Cognito BadRequest Troubleshooting Checklist

## Current Configuration Status

✅ **Domain Fixed**: Now using correct OAuth domain format
✅ **Client Secret**: Added to .env file  
⚠️  **Need to Verify**: The following items in your AWS Cognito console

## AWS Cognito Console Checklist

### 1. App Client Settings (User Pool → App clients → Your app)
- [ ] **OAuth 2.0 Grant Types**: ✅ Authorization code grant
- [ ] **OAuth 2.0 Flows**: ✅ Authorization code grant  
- [ ] **OAuth Scopes**: ✅ openid, ✅ email, ✅ phone

### 2. App Integration → App client settings
- [ ] **Callback URLs**: Must include exactly:
  - `http://localhost:8000/authorize/`
  - `http://127.0.0.1:8000/authorize/`
- [ ] **Sign out URLs**: Must include:
  - `http://localhost:8000/`
  - `http://127.0.0.1:8000/`

### 3. Domain Configuration
- [ ] **Domain exists**: `eu-west-2edujb1udy.auth.eu-west-2.amazoncognito.com`
- [ ] **Domain is active**: Should show "Active" status

### 4. Common Issues from Stack Overflow
- [ ] **Case sensitivity**: URLs must match exactly (including trailing slashes)
- [ ] **Protocol**: Must use `http://` for localhost (not `https://`)
- [ ] **Port**: Must match exactly (8000)
- [ ] **Client ID**: Verify it matches in both AWS and code

## Test Command
After verifying the above, test with:
```bash
curl -v "https://eu-west-2edujb1udy.auth.eu-west-2.amazoncognito.com/oauth2/authorize?response_type=code&client_id=1ljab4cb2oub8qb8bm33krrihb&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauthorize%2F&scope=openid+email+phone&state=test"
```

This should redirect to the login page, NOT return BadRequest.
