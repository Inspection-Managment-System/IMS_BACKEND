#!/usr/bin/env python3
"""
License Generator for IMS Backend
This script generates a new encrypted license file with a specified expiration date.
"""

import json
import os
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Use the same secret key as in the license.py file
SECRET_KEY = b"A\x80'\ncX1\xbf\x10q\x9c\xbb\x17\xba\xa2\x9b"

def encrypt(data):
    """Encrypt data using AES encryption"""
    # Generate a random IV
    iv = os.urandom(AES.block_size)
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    
    # Pad the data and encrypt
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # Return IV + encrypted data
    return iv + encrypted_data

def generate_license(expiration_date=None, company_name="Your Company", license_type="Standard"):
    """
    Generate a new license file
    
    Args:
        expiration_date (str): Expiration date in YYYY-MM-DD format (default: 1 year from now)
        company_name (str): Company name for the license
        license_type (str): Type of license (Standard, Premium, etc.)
    """
    
    # Set default expiration date to 1 year from now if not provided
    if not expiration_date:
        expiration_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    
    # Create license data
    license_data = {
        "company_name": company_name,
        "license_type": license_type,
        "issued_date": datetime.now().strftime("%Y-%m-%d"),
        "expiration_date": expiration_date,
        "features": [
            "user_management",
            "inspection_management", 
            "equipment_management",
            "reporting",
            "document_management"
        ],
        "max_users": 100,
        "version": "1.0"
    }
    
    # Convert to JSON string
    json_data = json.dumps(license_data, indent=2)
    
    # Encrypt the data
    encrypted_data = encrypt(json_data)
    
    # Write to file
    with open("license_v1.json", "wb") as f:
        f.write(encrypted_data)
    
    print("✅ License generated successfully!")
    print(f"📅 Expiration Date: {expiration_date}")
    print(f"🏢 Company: {company_name}")
    print(f"📋 License Type: {license_type}")
    print(f"📁 File: license_v1.json")
    
    return license_data

def main():
    print("🔐 IMS Backend License Generator")
    print("=" * 40)
    
    # Get user input
    company_name = input("Enter company name (or press Enter for default): ").strip() or "Your Company"
    license_type = input("Enter license type (or press Enter for 'Standard'): ").strip() or "Standard"
    
    # Ask for expiration date
    print("\nExpiration date options:")
    print("1. 1 year from now (default)")
    print("2. 6 months from now")
    print("3. 2 years from now")
    print("4. Custom date")
    
    choice = input("\nSelect option (1-4, default is 1): ").strip() or "1"
    
    expiration_date = None
    
    if choice == "2":
        expiration_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
    elif choice == "3":
        expiration_date = (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d")
    elif choice == "4":
        while True:
            custom_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
            try:
                # Validate date format
                datetime.strptime(custom_date, "%Y-%m-%d")
                expiration_date = custom_date
                break
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD")
    
    # Generate the license
    try:
        license_data = generate_license(expiration_date, company_name, license_type)
        
        print("\n🎉 License file created successfully!")
        print("You can now restart your Django server and the license error should be resolved.")
        
    except Exception as e:
        print(f"❌ Error generating license: {str(e)}")
        print("Make sure you have the required dependencies installed:")
        print("pip install pycryptodome")

if __name__ == "__main__":
    main()
