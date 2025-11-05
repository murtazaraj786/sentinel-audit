# Sentinel SOC Optimization Audit Tool

Queries the SOC Optimization blade in Microsoft Sentinel and exports optimization recommendations, rule efficiency metrics, and data ingestion analysis.

## 🎯 What it analyzes

### **Rule Efficiency**
- True positive vs false positive rates
- Alert volume and trends
- Rule performance metrics
- Efficiency ratings per rule

### **Data Ingestion Optimization**
- Data volume by type and solution
- Ingestion trends and patterns
- Cost optimization opportunities
- Storage utilization

### **SOC Recommendations**
- High false positive rules needing tuning
- Low-performing detection rules
- Data retention optimization
- Coverage gap analysis

## 🚀 Quick Setup

1. **Install dependencies**:
   ```powershell
   pip install -r soc_requirements.txt
   ```

2. **Set environment variables** (same as main audit tool):
   ```powershell
   $env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
   $env:RESOURCE_GROUP_NAME = "your-resource-group"
   $env:WORKSPACE_NAME = "your-sentinel-workspace-name"
   $env:AUTH_MODE = "device"
   ```

3. **Run the SOC optimization audit**:
   ```powershell
   python soc_optimization_audit.py
   ```

## 📊 Generated Reports

- **`soc_rule_efficiency_TIMESTAMP.csv`** - Rule performance analysis
- **`soc_data_ingestion_TIMESTAMP.csv`** - Data volume and cost analysis  
- **`soc_recommendations_TIMESTAMP.csv`** - Actionable optimization recommendations

## 🔍 Sample Metrics

### Rule Efficiency Report
- Rule name and product
- Total alerts generated
- True/false positive counts and rates
- Efficiency rating (Excellent/Good/Fair/Needs Review)

### Data Ingestion Report
- Data type and solution
- 30-day volume in GB
- Daily average ingestion
- Volume category (High/Medium/Low)

### Recommendations Report
- Category (Rule Optimization, Data Management, Coverage)
- Impact level (High/Medium/Low)
- Specific actions to improve SOC efficiency

## 🔐 Authentication

Uses the same authentication methods as the main audit tool:
- Device code authentication (`AUTH_MODE=device`)
- Browser authentication (`AUTH_MODE=browser`)  
- Service principal (for automation)
- Azure CLI default credentials

## 📈 Use Cases

- **Monthly SOC reviews** - Identify optimization opportunities
- **Rule tuning** - Find high false positive rules
- **Cost optimization** - Analyze data ingestion patterns
- **Performance monitoring** - Track detection effectiveness
- **Compliance reporting** - Document SOC efficiency metrics

## ⚠️ Requirements

- **Reader permissions** on Sentinel workspace
- **Log Analytics Reader** permissions for KQL queries
- Access to SecurityAlert and Usage tables
- 30 days of historical data for meaningful analysis