#!/usr/bin/env python3
"""
Sentinel SOC Optimization Audit Script
Exports SOC optimization recommendations and metrics from Microsoft Sentinel.
"""

import os
import csv
import sys
from datetime import datetime
from azure.identity import DefaultAzureCredential, ClientSecretCredential, InteractiveBrowserCredential, DeviceCodeCredential
from azure.mgmt.securityinsight import SecurityInsights
from azure.mgmt.operationalinsights import LogAnalyticsManagementClient
from azure.core.exceptions import AzureError
import requests

# Configuration
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.getenv('RESOURCE_GROUP_NAME')
WORKSPACE_NAME = os.getenv('WORKSPACE_NAME')

# Optional service principal authentication
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

def get_azure_credential():
    """Get Azure credentials with interactive options."""
    
    # Check for authentication mode preference
    auth_mode = os.getenv('AUTH_MODE', 'auto').lower()
    
    if auth_mode == 'device':
        print("🔐 Using Device Code authentication")
        print("📱 You'll be prompted to visit a URL and enter a code")
        return DeviceCodeCredential()
    
    elif auth_mode == 'browser':
        print("🌐 Using Interactive Browser authentication")
        print("🖥️  A browser window will open for authentication")
        return InteractiveBrowserCredential()
    
    elif all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        print("🔑 Using Service Principal authentication")
        return ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    
    else:
        print("🔄 Using Default Azure Credential (trying Azure CLI first)")
        print("💡 If this fails, set AUTH_MODE=device or AUTH_MODE=browser")
        return DefaultAzureCredential()

def get_workspace_id(log_client):
    """Get the workspace ID for Log Analytics queries."""
    try:
        workspace = log_client.workspaces.get(
            resource_group_name=RESOURCE_GROUP,
            workspace_name=WORKSPACE_NAME
        )
        return workspace.customer_id
    except Exception as e:
        print(f"Error getting workspace ID: {e}")
        return None

def query_log_analytics(credential, workspace_id, query):
    """Execute a KQL query against Log Analytics."""
    try:
        # Get access token for Log Analytics
        token_response = credential.get_token("https://api.loganalytics.io/.default")
        access_token = token_response.token
        
        # Prepare the query request
        url = f"https://api.loganalytics.io/v1/workspaces/{workspace_id}/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "query": query,
            "timespan": "P30D"  # Last 30 days
        }
        
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        
        return response.json()
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def audit_rule_efficiency(credential, workspace_id):
    """Audit analytic rule efficiency and performance."""
    print("Analyzing rule efficiency...")
    
    # KQL query to get rule performance metrics
    query = """
    SecurityAlert
    | where TimeGenerated >= ago(30d)
    | summarize 
        AlertCount = count(),
        UniqueAlerts = dcount(SystemAlertId),
        TruePositives = countif(Status == "Resolved" and Classification == "TruePositive"),
        FalsePositives = countif(Status == "Resolved" and Classification == "FalsePositive"),
        InProgress = countif(Status == "InProgress"),
        New = countif(Status == "New")
        by AlertName, ProductName, Severity
    | extend 
        TruePositiveRate = round(todouble(TruePositives) / todouble(AlertCount) * 100, 2),
        FalsePositiveRate = round(todouble(FalsePositives) / todouble(AlertCount) * 100, 2)
    | order by AlertCount desc
    | limit 100
    """
    
    result = query_log_analytics(credential, workspace_id, query)
    if not result or 'tables' not in result:
        return []
    
    rules = []
    if result['tables'] and len(result['tables']) > 0:
        table = result['tables'][0]
        columns = [col['name'] for col in table['columns']]
        
        for row in table['rows']:
            rule_data = dict(zip(columns, row))
            
            # Determine efficiency rating
            tp_rate = rule_data.get('TruePositiveRate', 0) or 0
            fp_rate = rule_data.get('FalsePositiveRate', 0) or 0
            
            if tp_rate > 80:
                efficiency = "Excellent"
            elif tp_rate > 60:
                efficiency = "Good"
            elif tp_rate > 40:
                efficiency = "Fair"
            else:
                efficiency = "Needs Review"
            
            rules.append({
                'RuleName': rule_data.get('AlertName', 'Unknown'),
                'Product': rule_data.get('ProductName', 'Unknown'),
                'Severity': rule_data.get('Severity', 'Unknown'),
                'TotalAlerts': rule_data.get('AlertCount', 0),
                'TruePositives': rule_data.get('TruePositives', 0),
                'FalsePositives': rule_data.get('FalsePositives', 0),
                'TruePositiveRate': f"{tp_rate}%",
                'FalsePositiveRate': f"{fp_rate}%",
                'Efficiency': efficiency
            })
    
    print(f"Analyzed {len(rules)} rules")
    return rules

def audit_data_ingestion(credential, workspace_id):
    """Audit data ingestion patterns and volumes."""
    print("Analyzing data ingestion...")
    
    # KQL query for data ingestion analysis
    query = """
    Usage
    | where TimeGenerated >= ago(30d)
    | where IsBillable == true
    | summarize 
        TotalGB = round(sum(Quantity) / 1024, 2),
        DailyAverageGB = round(sum(Quantity) / 1024 / 30, 2),
        RecordCount = sum(Quantity * 1024 * 1024)
        by DataType, Solution
    | order by TotalGB desc
    | limit 50
    """
    
    result = query_log_analytics(credential, workspace_id, query)
    if not result or 'tables' not in result:
        return []
    
    ingestion = []
    if result['tables'] and len(result['tables']) > 0:
        table = result['tables'][0]
        columns = [col['name'] for col in table['columns']]
        
        for row in table['rows']:
            data = dict(zip(columns, row))
            
            total_gb = data.get('TotalGB', 0) or 0
            
            # Categorize ingestion volume
            if total_gb > 100:
                volume_category = "High"
            elif total_gb > 10:
                volume_category = "Medium"
            elif total_gb > 1:
                volume_category = "Low"
            else:
                volume_category = "Very Low"
            
            ingestion.append({
                'DataType': data.get('DataType', 'Unknown'),
                'Solution': data.get('Solution', 'Unknown'),
                'TotalGB_30Days': total_gb,
                'DailyAverageGB': data.get('DailyAverageGB', 0) or 0,
                'VolumeCategory': volume_category
            })
    
    print(f"Analyzed {len(ingestion)} data types")
    return ingestion

def get_optimization_recommendations(rules, ingestion):
    """Generate optimization recommendations based on analysis."""
    print("Generating optimization recommendations...")
    
    recommendations = []
    
    # Rule-based recommendations
    high_fp_rules = [r for r in rules if float(r['FalsePositiveRate'].replace('%', '')) > 50]
    low_tp_rules = [r for r in rules if float(r['TruePositiveRate'].replace('%', '')) < 20]
    
    if high_fp_rules:
        recommendations.append({
            'Category': 'Rule Optimization',
            'Type': 'High False Positive Rate',
            'Description': f'{len(high_fp_rules)} rules have >50% false positive rate',
            'Impact': 'High',
            'Action': 'Review and tune rule logic to reduce false positives'
        })
    
    if low_tp_rules:
        recommendations.append({
            'Category': 'Rule Optimization',
            'Type': 'Low True Positive Rate',
            'Description': f'{len(low_tp_rules)} rules have <20% true positive rate',
            'Impact': 'Medium',
            'Action': 'Evaluate rule effectiveness and consider disabling or improving'
        })
    
    # Data ingestion recommendations
    high_volume_data = [d for d in ingestion if d['VolumeCategory'] == 'High']
    if high_volume_data:
        recommendations.append({
            'Category': 'Data Management',
            'Type': 'High Volume Ingestion',
            'Description': f'{len(high_volume_data)} data types consuming >100GB/month',
            'Impact': 'High',
            'Action': 'Review data retention policies and filtering rules'
        })
    
    # Coverage recommendations
    if len(rules) < 10:
        recommendations.append({
            'Category': 'Coverage',
            'Type': 'Low Rule Coverage',
            'Description': 'Limited number of active detection rules',
            'Impact': 'High',
            'Action': 'Enable more detection rules from Sentinel rule templates'
        })
    
    print(f"Generated {len(recommendations)} recommendations")
    return recommendations

def export_to_csv(data, filename, fieldnames):
    """Export data to CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ Exported {len(data)} records to {filename}")
    except Exception as e:
        print(f"❌ Error writing to {filename}: {e}")

def main():
    """Main function."""
    print("🎯 Microsoft Sentinel SOC Optimization Audit")
    print("=" * 60)
    
    # Check for .env file and load it
    env_file = '.env'
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"📁 Loaded configuration from {env_file}")
    
    # Check required environment variables
    if not all([SUBSCRIPTION_ID, RESOURCE_GROUP, WORKSPACE_NAME]):
        print("❌ Missing required environment variables:")
        print("   AZURE_SUBSCRIPTION_ID")
        print("   RESOURCE_GROUP_NAME") 
        print("   WORKSPACE_NAME")
        print()
        print("💡 Authentication Options:")
        print("   AUTH_MODE=device   - Device code authentication")
        print("   AUTH_MODE=browser  - Browser-based authentication")
        print("   (or use Azure CLI: az login)")
        sys.exit(1)
    
    print(f"Subscription: {SUBSCRIPTION_ID}")
    print(f"Resource Group: {RESOURCE_GROUP}")
    print(f"Workspace: {WORKSPACE_NAME}")
    print()
    
    try:
        # Get credentials and create clients
        credential = get_azure_credential()
        sentinel_client = SecurityInsights(credential, SUBSCRIPTION_ID)
        log_client = LogAnalyticsManagementClient(credential, SUBSCRIPTION_ID)
        
        # Get workspace ID for Log Analytics queries
        workspace_id = get_workspace_id(log_client)
        if not workspace_id:
            print("❌ Could not get workspace ID")
            sys.exit(1)
        
        print(f"Workspace ID: {workspace_id}")
        print()
        
        # Perform SOC optimization analysis
        rules = audit_rule_efficiency(credential, workspace_id)
        ingestion = audit_data_ingestion(credential, workspace_id)
        recommendations = get_optimization_recommendations(rules, ingestion)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to CSV files
        if rules:
            rule_fields = ['RuleName', 'Product', 'Severity', 'TotalAlerts', 'TruePositives', 
                          'FalsePositives', 'TruePositiveRate', 'FalsePositiveRate', 'Efficiency']
            export_to_csv(rules, f'soc_rule_efficiency_{timestamp}.csv', rule_fields)
        
        if ingestion:
            ingestion_fields = ['DataType', 'Solution', 'TotalGB_30Days', 'DailyAverageGB', 'VolumeCategory']
            export_to_csv(ingestion, f'soc_data_ingestion_{timestamp}.csv', ingestion_fields)
        
        if recommendations:
            rec_fields = ['Category', 'Type', 'Description', 'Impact', 'Action']
            export_to_csv(recommendations, f'soc_recommendations_{timestamp}.csv', rec_fields)
        
        print()
        print("✅ SOC Optimization audit completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Rules Analyzed: {len(rules)}")
        print(f"   - Data Types: {len(ingestion)}")
        print(f"   - Recommendations: {len(recommendations)}")
        
        # Show top recommendations
        if recommendations:
            print()
            print("🎯 Top Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. [{rec['Impact']}] {rec['Description']}")
        
    except AzureError as e:
        print(f"❌ Azure error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()