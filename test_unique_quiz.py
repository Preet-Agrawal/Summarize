#!/usr/bin/env python3
"""
Test script to verify unique quiz generation for different stories
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the generate function from app
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import generate_free_response

# Test with multiple different stories
stories = [
    """
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
    """,
    
    """
    In a small village near the mountains, there lived a brave knight named Sir Robert. 
    He was known throughout the kingdom for his courage and loyalty. One morning, 
    a messenger arrived with urgent news: a dragon had been terrorizing nearby towns. 
    Sir Robert immediately set out on his horse Thunder to face the beast. After 
    three days of travel, he reached the dragon's lair in the Black Mountains. 
    The battle was fierce, with fire and sword clashing for hours. Using his wit 
    and skill, Sir Robert managed to defeat the dragon and save the kingdom. 
    The people celebrated his return with a grand feast that lasted three days.
    """,
    
    """
    Sarah was a brilliant scientist working in a top-secret laboratory. She had been 
    developing a revolutionary time machine for the past decade. Finally, on a rainy 
    Tuesday evening, she completed her invention. Excited but nervous, Sarah decided 
    to test it herself. She set the coordinates for Victorian London, 1888. In a 
    flash of blue light, she found herself standing on a foggy street, surrounded 
    by horse-drawn carriages and gas lamps. During her adventure, she met famous 
    historical figures and witnessed events she had only read about in books. After 
    24 hours, her device automatically returned her to the present, where she 
    discovered that her journey had changed history in unexpected ways.
    """
]

print("Testing unique quiz generation for different stories...")
print("=" * 70)

for i, story in enumerate(stories, 1):
    print(f"\nSTORY {i}:")
    print("-" * 50)
    print(story[:200] + "..." if len(story) > 200 else story)
    print("\nGenerated Quiz Questions:")
    print("-" * 50)
    
    result = generate_free_response(story)
    
    # Extract just the quiz part
    if "QUIZ:" in result:
        quiz_part = result.split("QUIZ:")[1]
        # Show just the questions (not the full quiz with options)
        lines = quiz_part.split('\n')
        for line in lines:
            if line.strip() and line.strip()[0].isdigit() and '.' in line[:3]:
                print(f"  {line.strip()}")
    
    print()

print("=" * 70)
print("\n✓ Test Complete: Each story should have unique, context-specific questions!")
print("Note: Questions are dynamically generated based on characters, locations,")
print("      actions, and other elements found in each specific story.")