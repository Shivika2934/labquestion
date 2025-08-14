#!/usr/bin/env python3
"""
Test script to verify and fix automatic question generation
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add current directory to Python path
sys.path.insert(0, '.')

from app import app, db
from models import Topic, Question
from openai_service import generate_question_variations

def test_question_generation():
    """Test the complete question generation pipeline"""
    with app.app_context():
        print("=== Testing AI Question Generation System ===")
        
        # Get available topics
        topics = Topic.query.all()
        print(f"Available topics: {len(topics)}")
        for topic in topics:
            question_count = Question.query.filter_by(topic_id=topic.id).count()
            print(f"  - {topic.name} (ID: {topic.id}): {question_count} questions")
        
        # Test with the "stack and queues" topic (ID 4) which has no questions
        stack_topic = Topic.query.filter_by(name='stack and queues').first()
        if stack_topic:
            print(f"\nTesting generation for topic: {stack_topic.name}")
            
            base_question = "Implement stack and queue data structures with push, pop, enqueue, and dequeue operations. Include time complexity analysis and demonstrate practical applications in problem-solving scenarios."
            
            try:
                print("Calling OpenRouter API...")
                variations = generate_question_variations(
                    base_question=base_question,
                    topic_name=stack_topic.name,
                    difficulty=stack_topic.difficulty,
                    category=stack_topic.category,
                    num_variations=5
                )
                
                print(f"✓ Generated {len(variations)} question variations")
                
                # Save questions to database
                questions_saved = 0
                for i, variation in enumerate(variations):
                    question = Question(
                        topic_id=stack_topic.id,
                        question_text=variation['question'],
                        expected_answer=variation.get('expected_answer', ''),
                        difficulty=stack_topic.difficulty,
                        variation_number=i + 1,
                        is_assigned=False
                    )
                    db.session.add(question)
                    questions_saved += 1
                    print(f"  Question {i+1}: {variation['question'][:80]}...")
                
                db.session.commit()
                print(f"✓ Successfully saved {questions_saved} questions to database")
                
                # Verify in database
                final_count = Question.query.filter_by(topic_id=stack_topic.id).count()
                print(f"✓ Final question count for '{stack_topic.name}': {final_count}")
                
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("Stack and queues topic not found")
            return False

if __name__ == "__main__":
    success = test_question_generation()
    if success:
        print("\n🎉 Question generation system is working!")
    else:
        print("\n❌ Question generation system needs fixing")
    exit(0 if success else 1)