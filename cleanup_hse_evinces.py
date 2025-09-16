#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ims_backend.settings')
django.setup()

from inspection_management.models import Evince, InspectionResult, InspectionTest
from api.models import HSERiskAssessmentResult

def cleanup_hse_evinces():
    """Delete all HSE Risk Assessment evinces and related data"""
    
    print("=== CLEANING UP HSE RISK ASSESSMENT EVINCES ===")
    
    # Find all HSE Risk Assessment evinces
    hse_evinces = Evince.objects.filter(evince_type='hse_risk_management')
    print(f"Found {hse_evinces.count()} HSE Risk Assessment evinces")
    
    if hse_evinces.count() == 0:
        print("No HSE Risk Assessment evinces found. Nothing to delete.")
        return
    
    # Show what will be deleted
    print("\nEvinces to be deleted:")
    for evince in hse_evinces:
        print(f"  - Evince ID: {evince.id}, Name: {evince.name}, Status: {evince.status}")
    
    # Confirm deletion
    confirm = input(f"\nAre you sure you want to delete {hse_evinces.count()} HSE Risk Assessment evinces? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        return
    
    # Delete related data first
    total_deleted = 0
    
    for evince in hse_evinces:
        print(f"\nDeleting evince {evince.id}...")
        
        # Delete inspection results
        results = InspectionResult.objects.filter(evince=evince)
        results_count = results.count()
        results.delete()
        print(f"  - Deleted {results_count} inspection results")
        
        # Delete inspection tests
        tests = InspectionTest.objects.filter(evince=evince)
        tests_count = tests.count()
        tests.delete()
        print(f"  - Deleted {tests_count} inspection tests")
        
        # Delete HSE Risk Assessment results
        hse_results = HSERiskAssessmentResult.objects.filter(evince=evince)
        hse_results_count = hse_results.count()
        hse_results.delete()
        print(f"  - Deleted {hse_results_count} HSE risk assessment results")
        
        # Delete the evince itself
        evince.delete()
        print(f"  - Deleted evince {evince.id}")
        
        total_deleted += 1
    
    print(f"\n=== CLEANUP COMPLETE ===")
    print(f"Successfully deleted {total_deleted} HSE Risk Assessment evinces")
    print(f"All related inspection results, tests, and HSE data have been removed")

if __name__ == "__main__":
    cleanup_hse_evinces()
