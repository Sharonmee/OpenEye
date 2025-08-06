from django.conf import settings
import os

# AWS Cognito Configuration
COGNITO_REGION = 'eu-west-2'
COGNITO_USER_POOL_ID = 'eu-west-2_eDuJb1UDY'
COGNITO_CLIENT_ID = '1ljab4cb2oub8qb8bm33krrihb'
COGNITO_CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET', '<client secret>')

# Get Cognito domain from environment variable
COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')

# OAuth2 endpoints (these are the correct ones for Cognito App Client)
AUTHORIZATION_ENDPOINT = f'{COGNITO_DOMAIN}/oauth2/authorize'
TOKEN_ENDPOINT = f'{COGNITO_DOMAIN}/oauth2/token'
USERINFO_ENDPOINT = f'{COGNITO_DOMAIN}/oauth2/userInfo'
JWKS_URI = f'{COGNITO_DOMAIN}/.well-known/jwks.json'

# Scopes
SCOPES = ['openid', 'email', 'phone']