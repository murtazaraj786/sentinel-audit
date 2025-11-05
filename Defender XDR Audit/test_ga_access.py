#!/usr/bin/env python3
"""
Quick GA Test Script for Defender XDR
Tests if Global Administrator account can access security data
"""

import os
import requests
from azure.identity import InteractiveBrowserCredential, DeviceCodeCredential

def test_ga_access():
    print("🔑 Testing Global Administrator Access")
    print("=" * 40)
    
    # Use interactive auth for GA account
    print("🌐 Authenticating with Global Administrator account...")
    credential = DeviceCodeCredential()
    
    try:
        token = credential.get_token("https://graph.microsoft.com/.default")
        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json'
        }
        
        print("✅ Authentication successful")
        
        # Test endpoints that require different permissions
        endpoints = [
            ("User Profile", "https://graph.microsoft.com/v1.0/me"),
            ("Organization", "https://graph.microsoft.com/v1.0/organization"),
            ("Secure Score", "https://graph.microsoft.com/v1.0/security/secureScores?$top=1"),
            ("Security Alerts", "https://graph.microsoft.com/beta/security/alerts?$top=5"),
            ("Security Incidents", "https://graph.microsoft.com/beta/security/incidents?$top=5"),
            ("Attack Simulations", "https://graph.microsoft.com/v1.0/security/attackSimulation/simulations")
        ]
        
        results = {}
        
        for name, url in endpoints:
            print(f"\n🔍 Testing {name}...")
            try:
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('value', [data])) if 'value' in data else 1
                    print(f"✅ {name}: SUCCESS ({count} items)")
                    results[name] = "SUCCESS"
                else:
                    print(f"❌ {name}: {response.status_code} - {response.reason}")
                    results[name] = f"FAILED ({response.status_code})"
            except Exception as e:
                print(f"⚠️  {name}: Error - {str(e)[:50]}...")
                results[name] = "ERROR"
        
        # Summary
        print("\n" + "=" * 40)
        print("📊 GLOBAL ADMINISTRATOR ACCESS TEST RESULTS:")
        print("-" * 40)
        
        success_count = sum(1 for v in results.values() if v == "SUCCESS")
        total_tests = len(results)
        
        for endpoint, result in results.items():
            status = "✅" if result == "SUCCESS" else "❌"
            print(f"{status} {endpoint}: {result}")
        
        print("-" * 40)
        print(f"📈 Success Rate: {success_count}/{total_tests} ({success_count/total_tests*100:.0f}%)")
        
        if success_count >= 4:  # At least basic + some security data
            print("🎉 EXCELLENT! GA account has sufficient access for full audit")
            return True
        elif success_count >= 2:  # Basic access works
            print("⚠️  PARTIAL: GA account works but may need additional permissions")
            return False
        else:
            print("❌ INSUFFICIENT: GA account lacks required permissions")
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ga_access()
    
    if success:
        print("\n🚀 Ready to run full Defender XDR audit with GA account!")
        print("💡 Just run: python defender_xdr_audit.py")
    else:
        print("\n🔧 May need to adjust permissions or authentication method")