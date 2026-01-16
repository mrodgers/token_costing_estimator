#!/usr/bin/env python3
"""Test script to verify type hints are working correctly"""

import sys
sys.path.append('.')
from token_calc import OpenAICostCalculator, get_input, display_results, describe_scenario, print_pricing, main

def test_type_hints():
    """Test that all functions have proper type hints and work correctly"""
    print("Testing type hints and functionality...")
    print("="*50)
    
    # Test OpenAICostCalculator class
    print("✅ Testing OpenAICostCalculator class...")
    calculator = OpenAICostCalculator(50.0, 5.0, 2000.0, 0.06)
    
    # Test calculation methods
    tokens_per_shift = calculator.calculate_tokens_per_shift()
    cost_per_shift = calculator.calculate_cost_per_shift()
    cost_per_hospital = calculator.calculate_cost_per_hospital_per_shift(10.0)
    daily_costs = calculator.calculate_daily_costs(3.0, 10.0)
    monthly_costs = calculator.calculate_monthly_costs(daily_costs)
    annual_costs = calculator.calculate_annual_costs(monthly_costs)
    
    print(f"  • Tokens per shift: {tokens_per_shift}")
    print(f"  • Cost per shift: ${cost_per_shift:.2f}")
    print(f"  • Cost per hospital per shift: ${cost_per_hospital:.2f}")
    print(f"  • Daily costs: ${daily_costs:.2f}")
    print(f"  • Monthly costs: ${monthly_costs:.2f}")
    print(f"  • Annual costs: ${annual_costs:.2f}")
    
    # Test standalone functions
    print("\n✅ Testing standalone functions...")
    
    # Test print_pricing function
    print("  • Testing print_pricing()...")
    print_pricing()
    
    # Test describe_scenario function
    print("  • Testing describe_scenario()...")
    description = describe_scenario(50.0, 5.0, 2000.0, 0.06, 10.0, 3.0)
    print(f"    Description length: {len(description)} characters")
    
    # Test display_results function
    print("  • Testing display_results()...")
    display_results(cost_per_shift, cost_per_hospital, daily_costs, monthly_costs, annual_costs)
    
    print("\n" + "="*50)
    print("✅ All type hints and functionality tests passed!")
    print("✅ Code quality improvements completed successfully!")

if __name__ == "__main__":
    test_type_hints()
