#!/usr/bin/env python3
"""
Populate QA Automation Engineer / SET quizzes
Run this script to add specialized quizzes for QA Automation track
"""
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models_hierarchical as models

def populate_qa_automation_quizzes():
    """Populate quizzes for QA Automation Engineer / SET specialization"""
    db = SessionLocal()
    
    try:
        # Load quiz data
        with open('data/qa_automation_quizzes.json', 'r') as f:
            data = json.load(f)
        
        specialization_id = data['specialization_id']
        specialization_name = data['specialization_name']
        
        print(f"\n{'='*80}")
        print(f"Populating quizzes for: {specialization_name} (ID: {specialization_id})")
        print(f"{'='*80}\n")
        
        # Verify specialization exists
        spec = db.query(models.Specialization).filter(
            models.Specialization.id == specialization_id
        ).first()
        
        if not spec:
            print(f"❌ Error: Specialization with ID {specialization_id} not found!")
            return
        
        print(f"✓ Found specialization: {spec.name}\n")
        
        # Create quizzes
        for quiz_data in data['quizzes']:
            # Check if quiz already exists
            existing_quiz = db.query(models.Quiz).filter(
                models.Quiz.title == quiz_data['title'],
                models.Quiz.specialization_id == specialization_id
            ).first()
            
            if existing_quiz:
                print(f"⊙ Quiz already exists: {quiz_data['title']}")
                print(f"  Updating existing quiz (ID: {existing_quiz.id})...")
                quiz = existing_quiz
                
                # Delete old questions
                db.query(models.Question).filter(
                    models.Question.quiz_id == quiz.id
                ).delete()
                db.commit()
            else:
                # Create new quiz
                quiz = models.Quiz(
                    title=quiz_data['title'],
                    description=quiz_data['description'],
                    specialization_id=specialization_id,
                    difficulty_level=quiz_data['difficulty_level'],
                    time_limit_minutes=quiz_data['time_limit_minutes'],
                    passing_score=quiz_data['passing_score']
                )
                db.add(quiz)
                db.commit()
                db.refresh(quiz)
                print(f"✓ Created quiz: {quiz_data['title']} (ID: {quiz.id})")
            
            # Add questions
            question_count = 0
            for idx, question_data in enumerate(quiz_data['questions']):
                question = models.Question(
                    quiz_id=quiz.id,
                    question_text=question_data['question_text'],
                    question_type=question_data['question_type'],
                    points=question_data['points'],
                    order_index=idx + 1,
                    explanation=question_data.get('explanation', '')
                )
                db.add(question)
                db.commit()
                db.refresh(question)
                question_count += 1
                
                # Add options
                for opt_idx, option_data in enumerate(question_data['options']):
                    option = models.QuestionOption(
                        question_id=question.id,
                        option_text=option_data['option_text'],
                        is_correct=option_data['is_correct'],
                        order_index=opt_idx + 1
                    )
                    db.add(option)
                
                db.commit()
            
            print(f"  → Added {question_count} questions")
        
        print(f"\n{'='*80}")
        print(f"✅ Successfully populated {len(data['quizzes'])} quiz(zes) for {specialization_name}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_qa_automation_quizzes()
