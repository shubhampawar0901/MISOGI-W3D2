#!/usr/bin/env python3
"""
Test script for the tool-enhanced reasoning system.
Tests the tools without requiring an API key.
"""

import sys
import os

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from tools.math_tools import call_tool as call_math_tool
from tools.string_tools import call_tool as call_string_tool


def test_math_tools():
    """Test mathematical tools."""
    print("=" * 50)
    print("TESTING MATH TOOLS")
    print("=" * 50)
    
    tests = [
        ("square_root", [25], "Square root of 25"),
        ("average", [[18, 50]], "Average of [18, 50]"),
        ("add", [15, 25], "15 + 25"),
        ("multiply", [7, 8], "7 × 8"),
        ("power", [2, 3], "2^3"),
    ]
    
    for tool_name, args, description in tests:
        try:
            result = call_math_tool(tool_name, *args)
            print(f"✓ {description}: {result}")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")


def test_string_tools():
    """Test string analysis tools."""
    print("\n" + "=" * 50)
    print("TESTING STRING TOOLS")
    print("=" * 50)
    
    tests = [
        ("count_vowels", ["Multimodality"], "Vowels in 'Multimodality'"),
        ("count_letters", ["machine"], "Letters in 'machine'"),
        ("count_consonants", ["reasoning"], "Consonants in 'reasoning'"),
        ("count_words", ["Hello world"], "Words in 'Hello world'"),
        ("find_longest_word", ["The quick brown fox"], "Longest word in 'The quick brown fox'"),
    ]
    
    for tool_name, args, description in tests:
        try:
            result = call_string_tool(tool_name, *args)
            print(f"✓ {description}: {result}")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")


def test_example_queries():
    """Test the example queries from the problem statement."""
    print("\n" + "=" * 50)
    print("TESTING EXAMPLE QUERY COMPONENTS")
    print("=" * 50)
    
    print("Query 1: 'What's the square root of the average of 18 and 50?'")
    try:
        avg = call_math_tool("average", [18, 50])
        sqrt_result = call_math_tool("square_root", avg)
        print(f"  Step 1 - Average of 18 and 50: {avg}")
        print(f"  Step 2 - Square root of {avg}: {sqrt_result}")
        print(f"  ✓ Final answer: {sqrt_result}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\nQuery 2: 'How many vowels are in the word Multimodality?'")
    try:
        vowels = call_string_tool("count_vowels", "Multimodality")
        print(f"  ✓ Vowels in 'Multimodality': {vowels}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\nQuery 3: 'Is the number of letters in machine greater than the number of vowels in reasoning?'")
    try:
        letters_machine = call_string_tool("count_letters", "machine")
        vowels_reasoning = call_string_tool("count_vowels", "reasoning")
        comparison = letters_machine > vowels_reasoning
        print(f"  Letters in 'machine': {letters_machine}")
        print(f"  Vowels in 'reasoning': {vowels_reasoning}")
        print(f"  ✓ Is {letters_machine} > {vowels_reasoning}? {comparison}")
    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    """Run all tests."""
    print("TOOL-ENHANCED REASONING - COMPONENT TESTS")
    print("=" * 60)
    
    test_math_tools()
    test_string_tools()
    test_example_queries()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
    print("\nTo test the full LLM integration, set up your OpenAI API key in .env")
    print("and run: python main.py 'Your question here'")


if __name__ == "__main__":
    main()
