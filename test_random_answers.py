#!/usr/bin/env python3
"""
Test script to verify correct answers are randomly positioned
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
In a small village near the mountains, there lived a brave knight named Sir Robert. 
He was known throughout the kingdom for his courage and loyalty. One morning, 
a messenger arrived with urgent news: a dragon had been terrorizing nearby towns. 
Sir Robert immediately set out on his horse Thunder to face the beast. After 
three days of travel, he reached the dragon's lair in the Black Mountains. 
The battle was fierce, with fire and sword clashing for hours. Using his wit 
and skill, Sir Robert managed to defeat the dragon and save the kingdom. 
The people celebrated his return with a grand feast that lasted three days.
"""

print("Testing randomized correct answer positions...")
print("=" * 60)
print("Running the same story 3 times to see different answer positions:\n")

for run in range(1, 4):
    print(f"RUN {run}:")
    print("-" * 40)
    
    result = generate_free_response(test_story)
    
    # Extract the quiz part and show correct answer positions
    if "QUIZ:" in result:
        quiz_part = result.split("QUIZ:")[1]
        lines = quiz_part.split('\n')
        
        correct_positions = []
        current_question = None
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit() and '.' in line[:3]:
                current_question = line
                print(f"  {line}")
            elif line.startswith("Correct:"):
                correct_letter = line.split(":")[1].strip()
                correct_positions.append(correct_letter)
                print(f"    → Correct answer at position: {correct_letter}")
        
        print(f"\n  Answer positions for this run: {', '.join(correct_positions)}")
    
    print()

print("=" * 60)
print("\n✓ If working correctly, you should see different correct answer")
print("  positions (A, B, C, D) across different questions and runs!")