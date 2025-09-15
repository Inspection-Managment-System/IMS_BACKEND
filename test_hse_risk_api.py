#!/usr/bin/env python
"""
Test script for HSE Risk Assessment API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api_endpoints():
    """Test HSE Risk Assessment API endpoints"""
    
    print("🧪 Testing HSE Risk Assessment API Endpoints")
    print("=" * 50)
    
    # Test 1: Get workflow states
    print("\n1. Testing workflow states endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/hse_risk_assessments/workflow-states/")
        if response.status_code == 200:
            print("✅ Workflow states endpoint working")
            print(f"   Response: {len(response.json())} states available")
        else:
            print(f"❌ Workflow states endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing workflow states: {e}")
    
    # Test 2: Get risk levels
    print("\n2. Testing risk levels endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/hse_risk_assessments/risk-levels/")
        if response.status_code == 200:
            print("✅ Risk levels endpoint working")
            print(f"   Response: {len(response.json())} risk levels available")
        else:
            print(f"❌ Risk levels endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing risk levels: {e}")
    
    # Test 3: Get risk categories
    print("\n3. Testing risk categories endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/hse_risk_assessments/risk-categories/")
        if response.status_code == 200:
            print("✅ Risk categories endpoint working")
            print(f"   Response: {len(response.json())} categories available")
        else:
            print(f"❌ Risk categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing risk categories: {e}")
    
    # Test 4: Get dashboard stats
    print("\n4. Testing dashboard stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/hse_risk_assessments/dashboard-stats/")
        if response.status_code == 200:
            print("✅ Dashboard stats endpoint working")
            stats = response.json()
            print(f"   Total assessments: {stats.get('total_assessments', 0)}")
        else:
            print(f"❌ Dashboard stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing dashboard stats: {e}")
    
    # Test 5: List HSE risk assessments
    print("\n5. Testing list HSE risk assessments endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/hse_risk_assessments/")
        if response.status_code == 200:
            print("✅ List HSE risk assessments endpoint working")
            assessments = response.json()
            print(f"   Found {len(assessments)} assessments")
        else:
            print(f"❌ List HSE risk assessments endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing list assessments: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 HSE Risk Assessment API Testing Complete!")

if __name__ == "__main__":
    test_api_endpoints()
