"""
Automatic database initialization - populates data if database is empty
This runs automatically when the app starts
Loads data from JSON files in the data/ directory
"""
import sys
import os
import json
from pathlib import Path

# Get the path to the data directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models_hierarchical import Sector, Branch, Specialization, Quiz, Question, QuestionOption

def load_sectors_from_json():
    """Load sectors data from JSON file"""
    sectors_file = DATA_DIR / "sectors.json"
    if not sectors_file.exists():
        print(f"⚠️  Sectors JSON file not found at {sectors_file}")
        return None
    
    with open(sectors_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("sectors", [])

def load_quizzes_from_json():
    """Load quizzes data from JSON file"""
    quizzes_file = DATA_DIR / "quizzes.json"
    if not quizzes_file.exists():
        print(f"⚠️  Quizzes JSON file not found at {quizzes_file}")
        return None
    
    with open(quizzes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("quizzes", [])

def auto_populate_if_empty():
    """
    Automatically populate database with required data if tables are empty
    Loads data from JSON files in the data/ directory
    This ensures the app always has basic data to work with
    """
    db = SessionLocal()
    try:
        # Check if any sectors exist
        sector_count = db.query(Sector).count()
        
        if sector_count == 0:
            print("📊 Database is empty. Auto-populating from JSON files...")
            
            # Load sectors from JSON
            sectors_data = load_sectors_from_json()
            if not sectors_data:
                print("❌ Could not load sectors from JSON. Using fallback data.")
                return
            
            print(f"📂 Loading {len(sectors_data)} sector(s) from JSON...")
            
            # Process each sector from JSON
            for sector_data in sectors_data:
                # Create sector
                sector = Sector(
                    name=sector_data["name"],
                    description=sector_data["description"]
                )
                db.add(sector)
                db.commit()
                db.refresh(sector)
                print(f"✅ Created sector: {sector.name}")
                
                # Process branches for this sector
                for branch_data in sector_data.get("branches", []):
                    branch = Branch(
                        name=branch_data["name"],
                        description=branch_data["description"],
                        sector_id=sector.id
                    )
                    db.add(branch)
                    db.commit()
                    db.refresh(branch)
                    print(f"  ✅ Created branch: {branch.name}")
                    
                    # Process specializations for this branch
                    for spec_data in branch_data.get("specializations", []):
                        specialization = Specialization(
                            name=spec_data["name"],
                            description=spec_data["description"],
                            branch_id=branch.id
                        )
                        db.add(specialization)
                    db.commit()
                    print(f"    ✅ Added {len(branch_data.get('specializations', []))} specializations")
            
            print("✅ Created all sectors, branches, and specializations from JSON")
            
            # Now load quizzes from JSON
            quiz_count = db.query(Quiz).count()
            if quiz_count == 0:
                print("📝 Loading quizzes from JSON...")
                
                quizzes_data = load_quizzes_from_json()
                if quizzes_data:
                    for quiz_data in quizzes_data:
                        # Find specialization by name
                        specialization = db.query(Specialization).filter(
                            Specialization.name == quiz_data["specialization"]
                        ).first()
                        
                        if not specialization:
                            print(f"⚠️  Specialization '{quiz_data['specialization']}' not found. Skipping quiz: {quiz_data['title']}")
                            continue
                        
                        # Check if quiz already exists
                        existing_quiz = db.query(Quiz).filter(
                            Quiz.title == quiz_data["title"],
                            Quiz.specialization_id == specialization.id
                        ).first()
                        
                        if existing_quiz:
                            continue
                        
                        # Create quiz
                        quiz = Quiz(
                            title=quiz_data["title"],
                            description=quiz_data["description"],
                            specialization_id=specialization.id,
                            difficulty_level=quiz_data["difficulty_level"],
                            time_limit_minutes=quiz_data["time_limit_minutes"],
                            passing_score=quiz_data["passing_score"]
                        )
                        db.add(quiz)
                        db.commit()
                        db.refresh(quiz)
                        print(f"  ✅ Created quiz: {quiz.title}")
                        
                        # Create questions and options
                        for idx, q_data in enumerate(quiz_data.get("questions", [])):
                            question = Question(
                                quiz_id=quiz.id,
                                question_text=q_data["question_text"],
                                question_type=q_data["question_type"],
                                points=q_data.get("points", 1),
                                order_index=idx + 1,
                                explanation=q_data.get("explanation")
                            )
                            db.add(question)
                            db.flush()
                            
                            for opt_idx, option_data in enumerate(q_data.get("options", [])):
                                option = QuestionOption(
                                    question_id=question.id,
                                    option_text=option_data["text"],
                                    is_correct=option_data["is_correct"],
                                    order_index=opt_idx + 1
                                )
                                db.add(option)
                        
                        db.commit()
                        print(f"    ✅ Added {len(quiz_data.get('questions', []))} questions")
                    
                    print("✅ Created all quizzes from JSON")
                else:
                    print("⚠️  Could not load quizzes from JSON")
            
            print("✅ Auto-population complete from JSON files!")
            
        else:
            # Database has sectors, check if we need to add more sectors or quizzes
            # Load sectors from JSON and add any missing ones
            sectors_data = load_sectors_from_json()
            if sectors_data:
                added_sectors = 0
                for sector_data in sectors_data:
                    existing_sector = db.query(Sector).filter(Sector.name == sector_data["name"]).first()
                    
                    if not existing_sector:
                        # Create missing sector
                        sector = Sector(
                            name=sector_data["name"],
                            description=sector_data["description"]
                        )
                        db.add(sector)
                        db.commit()
                        db.refresh(sector)
                        print(f"✅ Added missing sector: {sector.name}")
                        added_sectors += 1
                        
                        # Add branches and specializations for new sector
                        for branch_data in sector_data.get("branches", []):
                            branch = Branch(
                                name=branch_data["name"],
                                description=branch_data["description"],
                                sector_id=sector.id
                            )
                            db.add(branch)
                            db.commit()
                            db.refresh(branch)
                            
                            for spec_data in branch_data.get("specializations", []):
                                specialization = Specialization(
                                    name=spec_data["name"],
                                    description=spec_data["description"],
                                    branch_id=branch.id
                                )
                                db.add(specialization)
                            db.commit()
                
                if added_sectors > 0:
                    print(f"📊 Added {added_sectors} new sector(s) from JSON")
            
            quiz_count = db.query(Quiz).count()
            
            # Try to load additional quizzes from JSON that might not exist
            quizzes_data = load_quizzes_from_json()
            if quizzes_data:
                added_count = 0
                for quiz_data in quizzes_data:
                    specialization = db.query(Specialization).filter(
                        Specialization.name == quiz_data["specialization"]
                    ).first()
                    
                    if not specialization:
                        continue
                    
                    existing_quiz = db.query(Quiz).filter(
                        Quiz.title == quiz_data["title"],
                        Quiz.specialization_id == specialization.id
                    ).first()
                    
                    if not existing_quiz:
                        # Create missing quiz
                        quiz = Quiz(
                            title=quiz_data["title"],
                            description=quiz_data["description"],
                            specialization_id=specialization.id,
                            difficulty_level=quiz_data["difficulty_level"],
                            time_limit_minutes=quiz_data["time_limit_minutes"],
                            passing_score=quiz_data["passing_score"]
                        )
                        db.add(quiz)
                        db.commit()
                        db.refresh(quiz)
                        
                        # Add questions
                        for idx, q_data in enumerate(quiz_data.get("questions", [])):
                            question = Question(
                                quiz_id=quiz.id,
                                question_text=q_data["question_text"],
                                question_type=q_data["question_type"],
                                points=q_data.get("points", 1),
                                order_index=idx + 1,
                                explanation=q_data.get("explanation")
                            )
                            db.add(question)
                            db.flush()
                            
                            for opt_idx, option_data in enumerate(q_data.get("options", [])):
                                option = QuestionOption(
                                    question_id=question.id,
                                    option_text=option_data["text"],
                                    is_correct=option_data["is_correct"],
                                    order_index=opt_idx + 1
                                )
                                db.add(option)
                        
                        db.commit()
                        added_count += 1
                
                if added_count > 0:
                    print(f"📝 Added {added_count} new quiz(zes) from JSON")
                else:
                    print(f"✅ Database already populated: {sector_count} sectors, {quiz_count} quizzes")
            else:
                print(f"✅ Database already populated: {sector_count} sectors, {quiz_count} quizzes")
                    
    except Exception as e:
        print(f"⚠️  Auto-population error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
