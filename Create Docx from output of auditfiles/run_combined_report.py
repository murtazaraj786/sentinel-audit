#!/usr/bin/env python3
"""
Combined Sentinel and Defender XDR Report Generator
This script demonstrates how to generate a comprehensive audit report
that includes both Sentinel and Defender XDR data.
"""

import subprocess
import sys
import os
import glob
from datetime import datetime

def find_latest_file(pattern):
    """Find the most recent file matching the given pattern."""
    files = glob.glob(pattern)
    if files:
        return max(files, key=os.path.getmtime)
    return None

def main():
    print("🔍 Combined Sentinel & Defender XDR Report Generator")
    print("=" * 60)
    
    # Required Sentinel files (these must be provided)
    required_sentinel_files = {
        "--analytic-rules": [
            "../Sentinel Audit/sentinel_analytic_rules_*.csv",
            "./sentinel_analytic_rules_*.csv"
        ],
        "--data-connectors": [
            "../Sentinel Audit/sentinel_data_connectors_*.csv", 
            "./sentinel_data_connectors_*.csv"
        ],
        "--soc-ingestion": [
            "../Sentinel SOC Optimisation Audit/soc_data_ingestion_*.csv",
            "./soc_data_ingestion_*.csv"
        ],
        "--soc-recommendations": [
            "../Sentinel SOC Optimisation Audit/soc_recommendations_*.csv",
            "./soc_recommendations_*.csv"
        ],
        "--soc-rule-efficiency": [
            "../Sentinel SOC Optimisation Audit/soc_rule_efficiency_*.csv",
            "./soc_rule_efficiency_*.csv"
        ]
    }
    
    # Optional Defender XDR files
    optional_xdr_files = {
        "--xdr-security-alerts": [
            "../Defender XDR Audit/defender_xdr_security_alerts_*.csv",
            "./defender_xdr_security_alerts_*.csv"
        ],
        "--xdr-security-incidents": [
            "../Defender XDR Audit/defender_xdr_security_incidents_*.csv",
            "./defender_xdr_security_incidents_*.csv"
        ],
        "--xdr-attack-simulations": [
            "../Defender XDR Audit/defender_xdr_attack_simulations_*.csv",
            "./defender_xdr_attack_simulations_*.csv"
        ],
        "--xdr-secure-score": [
            "../Defender XDR Audit/defender_xdr_secure_score_*.csv",
            "./defender_xdr_secure_score_*.csv"
        ]
    }
    
    # Build command arguments
    cmd_args = ["python", "generate_sentinel_hld_report.py"]
    
    # Find required Sentinel files
    missing_required = []
    for arg, patterns in required_sentinel_files.items():
        found_file = None
        for pattern in patterns:
            found_file = find_latest_file(pattern)
            if found_file:
                break
        
        if found_file:
            cmd_args.extend([arg, found_file])
            print(f"✅ Found {arg}: {found_file}")
        else:
            missing_required.append(arg)
            print(f"❌ Missing {arg} (patterns: {', '.join(patterns)})")
    
    if missing_required:
        print(f"\n❌ Cannot proceed - missing required files: {', '.join(missing_required)}")
        print("Please ensure you have run the Sentinel audits first.")
        return 1
    
    # Find optional XDR files
    xdr_files_found = 0
    for arg, patterns in optional_xdr_files.items():
        found_file = None
        for pattern in patterns:
            found_file = find_latest_file(pattern)
            if found_file:
                break
        
        if found_file:
            cmd_args.extend([arg, found_file])
            print(f"✅ Found {arg}: {found_file}")
            xdr_files_found += 1
        else:
            print(f"⚠️  Optional {arg} not found (patterns: {', '.join(patterns)})")
    
    # Set output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"combined_sentinel_xdr_audit_{timestamp}.docx"
    cmd_args.extend(["--output", output_filename])
    
    print(f"\n📊 Generating report with {xdr_files_found} XDR data sources...")
    print(f"📁 Output file: {output_filename}")
    print("\n" + "=" * 60)
    
    # Run the report generator
    try:
        result = subprocess.run(cmd_args, check=True, capture_output=True, text=True)
        print("✅ Report generated successfully!")
        print(f"📄 Report saved as: {output_filename}")
        
        if result.stdout:
            print(f"Output: {result.stdout}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating report: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return 1
    except FileNotFoundError:
        print("❌ Could not find generate_sentinel_hld_report.py")
        print("Please make sure you're running this from the correct directory.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())