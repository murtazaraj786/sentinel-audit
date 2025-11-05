#!/usr/bin/env python3
"""
Test Microsoft Graph API with basic permissions
"""

import os
import requests
from azure.identity import DeviceCodeCredential

def test_basic_graph_access():
    """Test basic Microsoft Graph API access."""
    print("🔐 Testing Device Code Authentication...")
    
    # Get tenant ID from environment
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    # Use device code credential
    credential = DeviceCodeCredential(tenant_id=tenant_id)
    
    try:
        # Get access token for Microsoft Graph
        token = credential.get_token("https://graph.microsoft.com/.default")
        print("✅ Device authentication successful!")
        
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        # Test basic user profile (should work with basic permissions)
        print("\n🧪 Testing basic Graph API access...")
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Successfully connected as: {user_data.get('displayName', 'Unknown')}")
            print(f"   Email: {user_data.get('mail', user_data.get('userPrincipalName', 'N/A'))}")
            print(f"   Job Title: {user_data.get('jobTitle', 'N/A')}")
            return True
        else:
            print(f"❌ Basic Graph API failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Device authentication failed: {e}")
        return False

def test_organization_info():
    """Test organization information access."""
    print("\n🏢 Testing organization information access...")
    
    tenant_id = os.getenv('AZURE_TENANT_ID')
    credential = DeviceCodeCredential(tenant_id=tenant_id)
    
    try:
        token = credential.get_token("https://graph.microsoft.com/.default")
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        # Try to get organization info
        response = requests.get(
            "https://graph.microsoft.com/v1.0/organization",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            org_data = response.json()
            if org_data.get('value'):
                org = org_data['value'][0]
                print(f"✅ Organization: {org.get('displayName', 'Unknown')}")
                print(f"   Tenant ID: {org.get('id', 'N/A')}")
                return True
        else:
            print(f"⚠️  Organization info not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Organization info failed: {e}")
        return False

if __name__ == "__main__":
    print("🛡️  Microsoft Graph API - Basic Access Test")
    print("=" * 50)
    
    # Test basic access
    basic_success = test_basic_graph_access()
    
    if basic_success:
        test_organization_info()
        
        print("\n" + "=" * 50)
        print("✅ Device authentication is working!")
        print("🔐 Your user account has basic Microsoft Graph access.")
        print("\n💡 The security API permissions (403/401 errors) are normal")
        print("   because your user account needs explicit security roles like:")
        print("   - Security Administrator")
        print("   - Security Reader") 
        print("   - Global Administrator")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Please complete the device login process first")
        print("🌐 Visit: https://microsoft.com/devicelogin")
        print("=" * 50)