#!/usr/bin/env python3
"""
Quick setup script for QuickBooks authentication with your app credentials
"""

from index import authenticate_quickbooks

# Your QuickBooks app credentials
CLIENT_ID = "ABOsn8UHXFIenxi8eoC0Q4EcZfNlqdHjuAnCd0Wioabt3DejDV"
CLIENT_SECRET = "89RS1m8IwSNRyVS0XrCOILnEqGKQdj7kFLfgibKt"
REDIRECT_URI = "https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl"  # Default for sandbox
ENVIRONMENT = "sandbox"

if __name__ == "__main__":
    print("Setting up QuickBooks authentication...")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Environment: {ENVIRONMENT}")
    
    try:
        result = authenticate_quickbooks(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            environment=ENVIRONMENT
        )
        
        print("\n" + "="*50)
        print("AUTHENTICATION SETUP COMPLETE")
        print("="*50)
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"\nNext step: {result['next_step']}")
        print(f"\nAuthorization URL:")
        print(result['auth_url'])
        print("\n" + "="*50)
        print("INSTRUCTIONS:")
        print("1. Click the authorization URL above")
        print("2. Log in to your QuickBooks sandbox account")
        print("3. Authorize the app")
        print("4. Copy the authorization code from the redirect")
        print("5. Use complete_authentication tool with the code")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")