"""
Complete database population script for Future of Work Readiness platform
This script populates ALL sectors mentioned in the requirements:
- Healthcare
- Finance  
- Technology
- Education 
- Retail
Each with their specializations and sample quizzes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from app.database import engine, Base
from app.models import Sector, Specialization, Quiz, Question, AnswerOption

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def populate_all_sectors():
    """Populate the database with all sector data"""
    db = SessionLocal()
    
    try:
        print("🚀 Starting complete database population...")
        
        # Define all sectors and their specializations
        sectors_data = {
            "Healthcare": {
                "description": "Healthcare sector covering medical professionals, nurses, technicians, and healthcare administration.",
                "specializations": [
                    {"name": "Medical Professionals", "description": "Doctors, specialists, surgeons, and medical practitioners"},
                    {"name": "Nursing", "description": "Registered nurses, nurse practitioners, and nursing specialists"},
                    {"name": "Healthcare Technology", "description": "Medical IT, health informatics, and healthcare software"},
                    {"name": "Healthcare Administration", "description": "Hospital management, healthcare policy, and medical administration"}
                ]
            },
            "Finance": {
                "description": "Financial sector covering banking, investment, accounting, and financial technology.",
                "specializations": [
                    {"name": "Banking & Lending", "description": "Commercial banking, lending, and financial services"},
                    {"name": "Investment & Trading", "description": "Investment analysis, trading, and portfolio management"},
                    {"name": "Accounting & Auditing", "description": "Financial accounting, auditing, and tax preparation"},
                    {"name": "Financial Technology", "description": "Fintech, blockchain, and financial software development"}
                ]
            },
            "Technology": {
                "description": "Technology sector covering software development, data science, cybersecurity, and IT infrastructure.",
                "specializations": [
                    {"name": "Software Development", "description": "Frontend, backend, full-stack, and mobile development"},
                    {"name": "Data Science & AI", "description": "Data analysis, machine learning, and artificial intelligence"},
                    {"name": "Cybersecurity", "description": "Information security, network security, and compliance"},
                    {"name": "IT Infrastructure", "description": "Cloud computing, DevOps, and system administration"},
                    {"name": "Frontend Development", "description": "User interface development with HTML, CSS, and JavaScript"}
                ]
            },
            "Education": {
                "description": "Education sector covering teaching, curriculum development, and educational technology.",
                "specializations": [
                    {"name": "Primary Education", "description": "Elementary and primary school teaching"},
                    {"name": "Secondary Education", "description": "High school and secondary education"},
                    {"name": "Higher Education", "description": "University, college, and academic research"},
                    {"name": "Educational Technology", "description": "EdTech, online learning, and educational software"}
                ]
            },
            "Retail": {
                "description": "Retail sector covering sales, merchandising, e-commerce, and retail management.",
                "specializations": [
                    {"name": "Sales & Customer Service", "description": "Retail sales, customer relations, and service"},
                    {"name": "Merchandising", "description": "Product merchandising, inventory, and visual displays"},
                    {"name": "E-commerce", "description": "Online retail, digital marketing, and e-commerce management"},
                    {"name": "Retail Management", "description": "Store management, operations, and retail strategy"}
                ]
            }
        }
        
        # Create sectors and specializations
        for sector_name, sector_info in sectors_data.items():
            # Check if sector already exists
            existing_sector = db.query(Sector).filter(Sector.name == sector_name).first()
            if existing_sector:
                print(f"✅ {sector_name} sector already exists")
                sector = existing_sector
            else:
                # Create new sector
                sector = Sector(
                    name=sector_name,
                    description=sector_info["description"]
                )
                db.add(sector)
                db.flush()
                print(f"✅ Created {sector_name} sector")
            
            # Create specializations for this sector
            for spec_data in sector_info["specializations"]:
                existing_spec = db.query(Specialization).filter(
                    Specialization.name == spec_data["name"],
                    Specialization.sector_id == sector.id
                ).first()
                
                if not existing_spec:
                    specialization = Specialization(
                        name=spec_data["name"],
                        description=spec_data["description"],
                        sector_id=sector.id
                    )
                    db.add(specialization)
                    print(f"  ✅ Created specialization: {spec_data['name']}")
        
        db.flush()
        
        # Create sample quizzes for Frontend Development (keep existing quiz content)
        frontend_spec = db.query(Specialization).filter(
            Specialization.name == "Frontend Development"
        ).first()
        
        if frontend_spec:
            # Create sample quiz if it doesn't exist
            existing_quiz = db.query(Quiz).filter(
                Quiz.specialization_id == frontend_spec.id
            ).first()
            
            if not existing_quiz:
                # Create a basic Level 1 quiz
                quiz = Quiz(
                    title="Frontend Development Basics - Level 1",
                    description="Basic frontend development concepts covering HTML, CSS, and JavaScript fundamentals",
                    specialization_id=frontend_spec.id,
                    difficulty_level=1,
                    duration_minutes=30
                )
                db.add(quiz)
                db.flush()
                
                # Add a few sample questions
                sample_questions = [
                    {
                        "text": "What does HTML stand for?",
                        "correct": "HyperText Markup Language",
                        "options": [
                            "HyperText Markup Language",
                            "High Tech Modern Language",
                            "Home Tool Markup Language",
                            "Hyperlink and Text Markup Language"
                        ]
                    },
                    {
                        "text": "Which CSS property is used to change the text color?",
                        "correct": "color",
                        "options": [
                            "text-color",
                            "font-color", 
                            "color",
                            "text-style"
                        ]
                    }
                ]
                
                for i, q_data in enumerate(sample_questions):
                    question = Question(
                        question_text=q_data["text"],
                        correct_answer=q_data["correct"],
                        quiz_id=quiz.id,
                        order_in_quiz=i + 1
                    )
                    db.add(question)
                    db.flush()
                    
                    # Add answer options
                    for j, option_text in enumerate(q_data["options"]):
                        answer_option = AnswerOption(
                            option_text=option_text,
                            question_id=question.id,
                            is_correct=(option_text == q_data["correct"])
                        )
                        db.add(answer_option)
                
                print("✅ Created sample Frontend Development quiz")
        
        # Commit all changes
        db.commit()
        print("\n🎉 Database population completed successfully!")
        print("\nSectors created:")
        
        # Display final summary
        sectors = db.query(Sector).all()
        for sector in sectors:
            spec_count = db.query(Specialization).filter(Specialization.sector_id == sector.id).count()
            quiz_count = db.query(Quiz).join(Specialization).filter(Specialization.sector_id == sector.id).count()
            print(f"  • {sector.name}: {spec_count} specializations, {quiz_count} quizzes")
            
    except Exception as e:
        print(f"❌ Error during population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_all_sectors()
