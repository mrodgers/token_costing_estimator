#!/usr/bin/env python3
"""Test script to verify export functionality"""

import sys
import os
from datetime import datetime
sys.path.append('.')
from token_calc import export_to_csv, export_to_json

def test_export_functions():
    """Test both CSV and JSON export functions"""
    print("Testing data export functionality...")
    print("="*50)
    
    # Create test data
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'prompts_per_shift': 50.0,
        'multiplier': 5.0,
        'avg_tokens_per_call': 2000.0,
        'token_cost_per_thousand': 0.06,
        'doctors_per_shift': 10.0,
        'shifts_per_day': 3.0,
        'cost_per_shift': 30.0,
        'cost_per_hospital_per_shift': 300.0,
        'daily_costs': 900.0,
        'monthly_costs': 27000.0,
        'annual_costs': 324000.0,
        'scenario_description': 'Test scenario for export functionality validation'
    }
    
    # Test CSV export
    try:
        csv_filename = export_to_csv(test_data, 'test_export.csv')
        print(f"✅ CSV export successful: {csv_filename}")
        
        # Verify file exists and has content
        if os.path.exists(csv_filename):
            with open(csv_filename, 'r') as f:
                content = f.read()
                if len(content) > 0:
                    print(f"   File size: {len(content)} characters")
                    print(f"   First line: {content.split(chr(10))[0]}")
                else:
                    print("   ❌ File is empty")
        else:
            print("   ❌ File was not created")
            
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
    
    # Test JSON export
    try:
        json_filename = export_to_json(test_data, 'test_export.json')
        print(f"✅ JSON export successful: {json_filename}")
        
        # Verify file exists and has content
        if os.path.exists(json_filename):
            with open(json_filename, 'r') as f:
                content = f.read()
                if len(content) > 0:
                    print(f"   File size: {len(content)} characters")
                    # Try to parse JSON to verify it's valid
                    import json
                    try:
                        json.loads(content)
                        print("   ✅ Valid JSON format")
                    except json.JSONDecodeError:
                        print("   ❌ Invalid JSON format")
                else:
                    print("   ❌ File is empty")
        else:
            print("   ❌ File was not created")
            
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
    
    print("="*50)
    print("Export functionality test completed!")

if __name__ == "__main__":
    test_export_functions()
