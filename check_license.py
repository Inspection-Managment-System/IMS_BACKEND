 #!/usr/bin/env python3
"""
License Checker for IMS Backend
This script checks the current license status and displays its details.
"""

import json
import os
from datetime import datetime
from ims_backend.utils.license import decrypt

def check_license():
    """Check the current license status"""
    
    print("🔍 IMS Backend License Checker")
    print("=" * 40)
    
    # Check if license file exists
    if not os.path.exists("license_v1.json"):
        print("❌ License file not found: license_v1.json")
        print("Please run generate_license.py to create a new license.")
        return False
    
    try:
        # Read and decrypt the license
        with open("license_v1.json", "rb") as file:
            encrypted_data = file.read()
            decrypted_data = decrypt(encrypted_data)
            license_data = json.loads(decrypted_data)
        
        # Display license information
        print("✅ License file found and valid!")
        print()
        print("📋 License Details:")
        print(f"   Company: {license_data.get('company_name', 'N/A')}")
        print(f"   Type: {license_data.get('license_type', 'N/A')}")
        print(f"   Issued: {license_data.get('issued_date', 'N/A')}")
        print(f"   Expires: {license_data.get('expiration_date', 'N/A')}")
        print(f"   Version: {license_data.get('version', 'N/A')}")
        print(f"   Max Users: {license_data.get('max_users', 'N/A')}")
        
        # Check expiration
        expiration_date_str = license_data.get("expiration_date")
        if expiration_date_str:
            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            if current_date > expiration_date:
                print()
                print("❌ LICENSE EXPIRED!")
                print(f"   Expired on: {expiration_date_str}")
                print("   Please generate a new license using generate_license.py")
                return False
            else:
                days_remaining = (expiration_date - current_date).days
                print()
                print("✅ License is valid!")
                print(f"   Days remaining: {days_remaining}")
                
                if days_remaining <= 30:
                    print("⚠️  Warning: License expires soon!")
                
                return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error reading license: {str(e)}")
        print("The license file may be corrupted or invalid.")
        return False

if __name__ == "__main__":
    check_license()
