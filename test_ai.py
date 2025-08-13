#!/usr/bin/env python3
"""
Test script for AI summarization and quiz generation
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the generate function from app
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import generate_free_response

# Test story
test_story = """
Once upon a time, there was a young girl named Alice who loved to explore. 
One day, she found a mysterious rabbit hole in her garden. Curious, she 
decided to follow the white rabbit down the hole. She fell for what seemed 
like hours before landing in a strange wonderland filled with talking animals 
and magical creatures. Alice met a grinning Cheshire Cat who could disappear 
at will, attended a mad tea party with the March Hare and the Mad Hatter, 
and even played croquet with the Queen of Hearts using flamingos as mallets. 
Throughout her journey, Alice learned that things aren't always what they seem 
and that imagination can take you to incredible places. In the end, she woke 
up under a tree, wondering if it had all been a dream.
"""

print("Testing AI story summarization and quiz generation...")
print("=" * 60)
print("Input Story:")
print(test_story)
print("=" * 60)

# Generate response
result = generate_free_response(test_story)

print("\nGenerated Output:")
print("=" * 60)
print(result)
print("=" * 60)

# Check if we have both summary and quiz
if "SUMMARY:" in result and "QUIZ:" in result:
    print("\n✓ SUCCESS: Both summary and quiz were generated!")
else:
    print("\n✗ WARNING: Output format may not be complete")
    if "SUMMARY:" not in result:
        print("  - Missing SUMMARY section")
    if "QUIZ:" not in result:
        print("  - Missing QUIZ section")

print("\nNote: For best results, ensure HUGGINGFACE_API_KEY is set in .env file")