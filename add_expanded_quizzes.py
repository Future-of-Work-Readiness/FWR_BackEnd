#!/usr/bin/env python3
"""
Script to add expanded quizzes with multiple levels to the database
Run this script to populate the database with comprehensive quizzes
"""

import json
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.database import SessionLocal, engine
from app import models_hierarchical as models

def load_quizzes_from_json(file_path):
    """Load quizzes from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['quizzes']

def get_specialization_id(db, specialization_name):
    """Get specialization ID by name"""
    spec = db.query(models.Specialization).filter(
        models.Specialization.name == specialization_name
    ).first()
    if spec:
        return spec.id
    print(f"Warning: Specialization '{specialization_name}' not found!")
    return None

def add_quizzes_to_database(json_file='data/expanded_quizzes.json'):
    """Add quizzes from JSON file to database"""
    db = SessionLocal()
    
    try:
        # Load quizzes from JSON
        quizzes_data = load_quizzes_from_json(json_file)
        print(f"📚 Loaded {len(quizzes_data)} quizzes from {json_file}")
        
        added_count = 0
        skipped_count = 0
        
        for quiz_data in quizzes_data:
            # Get specialization ID
            spec_id = get_specialization_id(db, quiz_data['specialization'])
            if not spec_id:
                print(f"❌ Skipping quiz '{quiz_data['title']}' - specialization not found")
                skipped_count += 1
                continue
            
            # Check if quiz already exists
            existing = db.query(models.Quiz).filter(
                models.Quiz.title == quiz_data['title'],
                models.Quiz.specialization_id == spec_id
            ).first()
            
            if existing:
                print(f"⏭️  Quiz '{quiz_data['title']}' already exists, skipping...")
                skipped_count += 1
                continue
            
            # Create quiz
            quiz = models.Quiz(
                title=quiz_data['title'],
                description=quiz_data['description'],
                specialization_id=spec_id,
                difficulty_level=quiz_data['difficulty_level'],
                time_limit_minutes=quiz_data['time_limit_minutes'],
                passing_score=quiz_data['passing_score'],
                is_active=True
            )
            db.add(quiz)
            db.flush()  # Get the quiz ID
            
            # Add questions
            for idx, question_data in enumerate(quiz_data['questions']):
                question = models.Question(
                    quiz_id=quiz.id,
                    question_text=question_data['question_text'],
                    question_type=question_data['question_type'],
                    points=question_data['points'],
                    order_index=idx,
                    explanation=question_data.get('explanation', ''),
                    is_active=True
                )
                db.add(question)
                db.flush()  # Get the question ID
                
                # Add options
                for opt_idx, option_data in enumerate(question_data['options']):
                    option = models.QuestionOption(
                        question_id=question.id,
                        option_text=option_data['text'],
                        is_correct=option_data['is_correct'],
                        order_index=opt_idx
                    )
                    db.add(option)
            
            db.commit()
            print(f"✅ Added quiz: {quiz_data['title']} (Level {quiz_data['difficulty_level']}) with {len(quiz_data['questions'])} questions")
            added_count += 1
        
        print(f"\n🎉 Summary:")
        print(f"   ✅ Added: {added_count} quizzes")
        print(f"   ⏭️  Skipped: {skipped_count} quizzes")
        print(f"   📊 Total in file: {len(quizzes_data)} quizzes")
        
        # Show current quiz counts by specialization
        print(f"\n📊 Quizzes by Specialization:")
        specs = db.query(models.Specialization).all()
        for spec in specs:
            count = db.query(models.Quiz).filter(
                models.Quiz.specialization_id == spec.id
            ).count()
            if count > 0:
                # Show breakdown by level
                level_counts = {}
                for level in [1, 2, 3, 4]:
                    level_count = db.query(models.Quiz).filter(
                        models.Quiz.specialization_id == spec.id,
                        models.Quiz.difficulty_level == level
                    ).count()
                    if level_count > 0:
                        level_counts[level] = level_count
                
                level_str = ", ".join([f"L{k}:{v}" for k, v in sorted(level_counts.items())])
                print(f"   {spec.name}: {count} total ({level_str})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Expanded Quiz Population Script")
    print("=" * 60)
    add_quizzes_to_database()
    print("=" * 60)
