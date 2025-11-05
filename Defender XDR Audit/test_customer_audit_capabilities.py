#!/usr/bin/env python3
"""
Test what security data we can access with current permissions
"""

import os
import requests
from azure.identity import DeviceCodeCredential

def test_endpoint(headers, endpoint, description):
    """Test a specific Graph API endpoint."""
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('value', [data])) if 'value' in data else 1
            print(f"✅ {description}: {count} items found")
            return True, count, data
        elif response.status_code == 403:
            print(f"🔒 {description}: Forbidden (need Security Reader role)")
            return False, 0, None
        elif response.status_code == 401:
            print(f"🔒 {description}: Unauthorized (need app permissions)")
            return False, 0, None
        else:
            print(f"⚠️  {description}: {response.status_code} - {response.text[:100]}")
            return False, 0, None
    except Exception as e:
        print(f"❌ {description}: Error - {str(e)[:100]}")
        return False, 0, None

def test_available_endpoints():
    """Test various Microsoft Graph endpoints to see what's accessible."""
    print("🔍 Testing available Microsoft Graph security endpoints...")
    
    tenant_id = os.getenv('AZURE_TENANT_ID')
    credential = DeviceCodeCredential(tenant_id=tenant_id)
    
    try:
        token = credential.get_token("https://graph.microsoft.com/.default")
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        # Test various endpoints
        endpoints_to_test = [
            # Basic organization info
            ("https://graph.microsoft.com/v1.0/organization", "Organization Information"),
            ("https://graph.microsoft.com/v1.0/me", "User Profile"),
            
            # Directory and users (might be accessible)
            ("https://graph.microsoft.com/v1.0/users?$top=5&$select=displayName,userPrincipalName,accountEnabled", "User Directory (sample)"),
            ("https://graph.microsoft.com/v1.0/groups?$top=5&$select=displayName,securityEnabled", "Security Groups (sample)"),
            ("https://graph.microsoft.com/v1.0/applications?$top=5&$select=displayName,appId", "Applications (sample)"),
            
            # Conditional Access (might need higher permissions)
            ("https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies?$top=5", "Conditional Access Policies"),
            
            # Device management
            ("https://graph.microsoft.com/v1.0/devices?$top=5&$select=displayName,operatingSystem,isManaged", "Managed Devices (sample)"),
            
            # Audit logs (might be accessible)
            ("https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$top=5", "Directory Audit Logs"),
            ("https://graph.microsoft.com/v1.0/auditLogs/signIns?$top=5", "Sign-in Logs"),
            
            # Security endpoints (likely to fail but worth testing)
            ("https://graph.microsoft.com/v1.0/security/secureScores?$top=1", "Microsoft Secure Score"),
            ("https://graph.microsoft.com/beta/security/alerts?$top=5", "Security Alerts"),
            ("https://graph.microsoft.com/beta/security/incidents?$top=5", "Security Incidents"),
            ("https://graph.microsoft.com/v1.0/security/attackSimulation/simulations?$top=5", "Attack Simulations"),
            
            # Identity Protection (likely to fail)
            ("https://graph.microsoft.com/v1.0/identityProtection/riskyUsers?$top=5", "Risky Users"),
            ("https://graph.microsoft.com/v1.0/identityProtection/riskDetections?$top=5", "Risk Detections"),
            
            # Privileged Identity Management
            ("https://graph.microsoft.com/v1.0/privilegedAccess/azureADGroups/roleDefinitions?$top=5", "PIM Role Definitions"),
        ]
        
        accessible_endpoints = []
        
        print("\n" + "="*80)
        for endpoint, description in endpoints_to_test:
            success, count, data = test_endpoint(headers, endpoint, description)
            if success:
                accessible_endpoints.append((description, count, endpoint, data))
        
        print("\n" + "="*80)
        print("📊 SUMMARY - What You CAN Audit:")
        print("="*80)
        
        if accessible_endpoints:
            for desc, count, endpoint, data in accessible_endpoints:
                print(f"✅ {desc}: {count} items")
                
                # Show sample data for interesting endpoints
                if "User Directory" in desc and data and 'value' in data:
                    print(f"   Sample users: {[u.get('displayName', 'N/A') for u in data['value'][:3]]}")
                elif "Security Groups" in desc and data and 'value' in data:
                    print(f"   Sample groups: {[g.get('displayName', 'N/A') for g in data['value'][:3]]}")
                elif "Applications" in desc and data and 'value' in data:
                    print(f"   Sample apps: {[a.get('displayName', 'N/A') for a in data['value'][:3]]}")
        else:
            print("❌ No additional endpoints accessible beyond basic user profile")
        
        print("\n" + "="*80)
        print("🔒 What You CANNOT Audit (Need Security Reader/Admin role):")
        print("="*80)
        print("❌ Microsoft Defender XDR security alerts and incidents")
        print("❌ Microsoft Secure Score detailed recommendations") 
        print("❌ Attack simulation training results")
        print("❌ Advanced threat protection data")
        print("❌ Identity Protection risk detections")
        print("❌ Privileged Identity Management assignments")
        
        return accessible_endpoints
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return []

def suggest_alternatives():
    """Suggest alternative audit approaches."""
    print("\n" + "="*80)
    print("💡 ALTERNATIVE AUDIT APPROACHES FOR CUSTOMERS:")
    print("="*80)
    
    print("\n🎯 1. MICROSOFT SENTINEL AUDITS (Try these first!)")
    print("   • Sentinel data connectors inventory")
    print("   • Analytic rules assessment") 
    print("   • SOC optimization analysis")
    print("   • These might work with your SOC Engineer role!")
    
    print("\n🔍 2. AZURE SECURITY CENTER / DEFENDER FOR CLOUD")
    print("   • Security recommendations")
    print("   • Compliance assessments")
    print("   • Resource security configurations")
    print("   • Vulnerability assessments")
    
    print("\n📊 3. AZURE RESOURCE AUDITS")
    print("   • Virtual machine configurations")
    print("   • Network security groups")
    print("   • Storage account security settings")
    print("   • Key vault access policies")
    
    print("\n🔐 4. AZURE AD BASIC AUDITS (What you CAN do)")
    print("   • User account inventory")
    print("   • Group membership analysis")
    print("   • Application registrations")
    print("   • Basic sign-in activity")
    
    print("\n📋 5. CUSTOM SECURITY ASSESSMENTS")
    print("   • Configuration baselines")
    print("   • Policy compliance checks")
    print("   • Resource tagging audits")
    print("   • Cost optimization recommendations")
    
    print("\n🎯 RECOMMENDATION:")
    print("   Start with the Sentinel audits - as a SOC Engineer,")
    print("   you likely have permissions for Sentinel workspace data!")

if __name__ == "__main__":
    print("🛡️  Customer Estate Audit - Permission Assessment")
    print("="*80)
    
    accessible = test_available_endpoints()
    suggest_alternatives()
    
    print("\n" + "="*80)
    print("🚀 NEXT STEPS:")
    print("="*80)
    print("1. Try the Sentinel audit tools (cd '../Sentinel Audit')")
    print("2. Test SOC optimization analysis")
    print("3. Request Security Reader role from customer admin for full XDR audit")
    print("4. Focus on Azure resource security assessments")
    print("="*80)