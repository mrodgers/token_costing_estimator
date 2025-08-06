#!/usr/bin/env python3
"""Test script to verify error handling improvements"""

import sys
import io
from contextlib import redirect_stdout, redirect_stderr
sys.path.append('.')
from token_calc import get_input

def test_get_input_with_empty_input():
    """Test get_input with empty input (should use default)"""
    print("Testing get_input with empty input...")
    
    # Simulate empty input
    original_input = input
    def mock_input(prompt):
        print(f"Mock input called with: {prompt}")
        return ""  # Empty input
    
    # Temporarily replace input function
    import builtins
    builtins.input = mock_input
    
    try:
        result = get_input("Test prompt", "default_value")
        print(f"✅ Empty input test passed. Result: {result}")
        assert result == "default_value"
    finally:
        # Restore original input function
        builtins.input = original_input

def test_get_input_with_whitespace():
    """Test get_input with whitespace input (should use default)"""
    print("Testing get_input with whitespace input...")
    
    # Simulate whitespace input
    original_input = input
    def mock_input(prompt):
        print(f"Mock input called with: {prompt}")
        return "   "  # Whitespace input
    
    # Temporarily replace input function
    import builtins
    builtins.input = mock_input
    
    try:
        result = get_input("Test prompt", "default_value")
        print(f"✅ Whitespace input test passed. Result: {result}")
        assert result == "default_value"
    finally:
        # Restore original input function
        builtins.input = original_input

def test_get_input_with_valid_input():
    """Test get_input with valid input"""
    print("Testing get_input with valid input...")
    
    # Simulate valid input
    original_input = input
    def mock_input(prompt):
        print(f"Mock input called with: {prompt}")
        return "user_value"
    
    # Temporarily replace input function
    import builtins
    builtins.input = mock_input
    
    try:
        result = get_input("Test prompt", "default_value")
        print(f"✅ Valid input test passed. Result: {result}")
        assert result == "user_value"
    finally:
        # Restore original input function
        builtins.input = original_input

if __name__ == "__main__":
    print("Testing error handling improvements...")
    print("="*50)
    
    test_get_input_with_empty_input()
    print()
    test_get_input_with_whitespace()
    print()
    test_get_input_with_valid_input()
    print()
    
    print("="*50)
    print("✅ All error handling tests passed!")
