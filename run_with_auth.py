#!/usr/bin/env python3
"""
Authentication Helper for Sentinel Audit Tools
Provides easy authentication options for all audit scripts.
"""

import os
import sys
import subprocess
from pathlib import Path

def set_auth_mode():
    """Interactive function to set authentication mode."""
    print("🔐 Azure Authentication Setup")
    print("=" * 50)
    print("This will set the authentication method for all audit scripts.")
    print()
    print("Available Authentication Methods:")
    print("1. 🌐 Interactive Browser Login")
    print("   - Opens a web browser for authentication")
    print("   - Best for desktop environments")
    print("   - Requires GUI access")
    print()
    print("2. 📱 Device Code Login") 
    print("   - Provides a code to enter on another device")
    print("   - Best for remote/headless environments")
    print("   - Works from any device with internet")
    print()
    print("3. 🔄 Azure CLI")
    print("   - Uses existing 'az login' session")
    print("   - Fastest if already logged in")
    print("   - Requires Azure CLI installed")
    print()
    print("4. ⚡ Let each script prompt individually")
    print("   - Each script will ask for authentication method")
    print("   - Most flexible but requires interaction")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                os.environ['AUTH_MODE'] = 'browser'
                print("✅ Set to Interactive Browser Login")
                print("🖥️  Browser windows will open for authentication")
                return 'browser'
            
            elif choice == '2':
                os.environ['AUTH_MODE'] = 'device'
                print("✅ Set to Device Code Login")
                print("📱 You'll get codes to enter on https://microsoft.com/devicelogin")
                return 'device'
            
            elif choice == '3':
                os.environ['AUTH_MODE'] = 'cli'
                print("✅ Set to Azure CLI authentication")
                print("💡 Make sure to run 'az login' first if you haven't already")
                return 'cli'
            
            elif choice == '4':
                if 'AUTH_MODE' in os.environ:
                    del os.environ['AUTH_MODE']
                print("✅ Authentication mode cleared")
                print("🔄 Each script will prompt for authentication method")
                return 'prompt'
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            return None

def run_script_with_auth(script_path, script_name):
    """Run a script with the chosen authentication method."""
    print(f"\n🚀 Running {script_name}...")
    print("-" * 40)
    
    try:
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            return False
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              cwd=os.path.dirname(script_path),
                              check=False)
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            return True
        else:
            print(f"❌ {script_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main function."""
    print("🛡️  Sentinel Audit Tools - Authentication Helper")
    print("=" * 60)
    
    # Get current directory
    current_dir = Path.cwd()
    
    # Define script paths
    scripts = {
        "Sentinel Audit": current_dir / "Sentinel Audit" / "sentinel_audit.py",
        "SOC Optimization Audit": current_dir / "Sentinel SOC Optimisation Audit" / "soc_optimization_audit.py", 
        "Defender XDR Audit": current_dir / "Defender XDR Audit" / "defender_xdr_audit.py"
    }
    
    # Check which scripts exist
    available_scripts = {}
    for name, path in scripts.items():
        if path.exists():
            available_scripts[name] = path
        else:
            print(f"⚠️  {name} script not found at {path}")
    
    if not available_scripts:
        print("❌ No audit scripts found. Make sure you're in the correct directory.")
        return 1
    
    print(f"\n📋 Found {len(available_scripts)} audit scripts:")
    for name in available_scripts.keys():
        print(f"  ✅ {name}")
    
    # Set authentication mode
    print("\n" + "=" * 60)
    auth_mode = set_auth_mode()
    
    if auth_mode is None:
        return 1
    
    # Ask if user wants to run scripts now
    print("\n" + "=" * 60)
    print("🎯 Ready to run audit scripts!")
    print("\nOptions:")
    print("1. Run all available scripts now")
    print("2. Run individual scripts")
    print("3. Exit (just set authentication mode)")
    
    while True:
        try:
            run_choice = input("\nEnter choice (1-3): ").strip()
            
            if run_choice == '1':
                print("\n🚀 Running all available audit scripts...")
                success_count = 0
                for name, path in available_scripts.items():
                    if run_script_with_auth(str(path), name):
                        success_count += 1
                
                print(f"\n📊 Summary: {success_count}/{len(available_scripts)} scripts completed successfully")
                break
            
            elif run_choice == '2':
                print("\n📋 Available scripts:")
                script_list = list(available_scripts.items())
                for i, (name, _) in enumerate(script_list, 1):
                    print(f"  {i}. {name}")
                
                while True:
                    try:
                        script_choice = input(f"\nChoose script to run (1-{len(script_list)}) or 'q' to quit: ").strip()
                        
                        if script_choice.lower() == 'q':
                            break
                        
                        script_idx = int(script_choice) - 1
                        if 0 <= script_idx < len(script_list):
                            name, path = script_list[script_idx]
                            run_script_with_auth(str(path), name)
                        else:
                            print(f"❌ Invalid choice. Please enter 1-{len(script_list)} or 'q'")
                    
                    except ValueError:
                        print(f"❌ Invalid input. Please enter a number 1-{len(script_list)} or 'q'")
                    except KeyboardInterrupt:
                        print("\n👋 Exiting...")
                        break
                break
            
            elif run_choice == '3':
                print("👋 Authentication mode set. You can now run individual scripts.")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
    
    print("\n✨ Done! Your authentication preference has been set.")
    if auth_mode != 'prompt':
        print(f"🔐 Authentication mode: {auth_mode.upper()}")
        print("💡 To change this later, run this script again or set the AUTH_MODE environment variable")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())