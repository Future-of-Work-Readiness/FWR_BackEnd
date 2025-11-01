#!/usr/bin/env python3
"""
Populate database with sample quizzes and questions for specializations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models_hierarchical import Base, Specialization, Quiz, Question, QuestionOption

# Create all tables
Base.metadata.create_all(bind=engine)

def populate_quizzes():
    db = SessionLocal()
    try:
        print("🚀 Starting quiz and question population...")
        
        # Find Frontend Development specialization
        frontend_spec = db.query(Specialization).filter(
            Specialization.name == "Frontend Development"
        ).first()
        
        if not frontend_spec:
            print("❌ Frontend Development specialization not found. Please run populate_hierarchical_data.py first.")
            return
        
        # Check if quiz already exists
        existing_quiz = db.query(Quiz).filter(
            Quiz.specialization_id == frontend_spec.id,
            Quiz.title.like("%Frontend Development Basics%")
        ).first()
        
        if existing_quiz:
            print("✅ Quiz already exists for Frontend Development")
            return
        
        # Create quiz for Frontend Development (Difficulty Level 1 - Beginner)
        quiz = Quiz(
            title="Frontend Development Basics - Level 1",
            description="Fundamental concepts of frontend development including HTML, CSS, and JavaScript basics",
            specialization_id=frontend_spec.id,
            difficulty_level=1,
            time_limit_minutes=30,
            passing_score=70.0
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        print(f"✅ Created quiz: {quiz.title} (ID: {quiz.id})")
        
        # Sample questions for Frontend Development
        questions_data = [
            {
                "question_text": "What does HTML stand for?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "HyperText Markup Language", "is_correct": True},
                    {"text": "High-level Text Markup Language", "is_correct": False},
                    {"text": "Hyperlink and Text Markup Language", "is_correct": False},
                    {"text": "Home Tool Markup Language", "is_correct": False}
                ],
                "points": 1,
                "explanation": "HTML stands for HyperText Markup Language, which is the standard markup language for creating web pages."
            },
            {
                "question_text": "Which CSS property is used to change the text color?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "text-color", "is_correct": False},
                    {"text": "font-color", "is_correct": False},
                    {"text": "color", "is_correct": True},
                    {"text": "text-style", "is_correct": False}
                ],
                "points": 1,
                "explanation": "The 'color' property is used to set the color of text in CSS."
            },
            {
                "question_text": "Which JavaScript method is used to add an element to the end of an array?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "push()", "is_correct": True},
                    {"text": "pop()", "is_correct": False},
                    {"text": "shift()", "is_correct": False},
                    {"text": "unshift()", "is_correct": False}
                ],
                "points": 1,
                "explanation": "The push() method adds one or more elements to the end of an array and returns the new length."
            },
            {
                "question_text": "What is the purpose of CSS?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "To structure web pages", "is_correct": False},
                    {"text": "To style and layout web pages", "is_correct": True},
                    {"text": "To add interactivity to web pages", "is_correct": False},
                    {"text": "To connect to databases", "is_correct": False}
                ],
                "points": 1,
                "explanation": "CSS (Cascading Style Sheets) is used to style and layout web pages, controlling the visual appearance."
            },
            {
                "question_text": "Which HTML tag is used to create a hyperlink?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "<link>", "is_correct": False},
                    {"text": "<a>", "is_correct": True},
                    {"text": "<href>", "is_correct": False},
                    {"text": "<url>", "is_correct": False}
                ],
                "points": 1,
                "explanation": "The <a> tag (anchor tag) is used to create hyperlinks in HTML."
            },
            {
                "question_text": "What is React primarily used for?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "Styling web pages", "is_correct": False},
                    {"text": "Building user interfaces", "is_correct": True},
                    {"text": "Managing databases", "is_correct": False},
                    {"text": "Server-side rendering only", "is_correct": False}
                ],
                "points": 1,
                "explanation": "React is a JavaScript library primarily used for building user interfaces, especially for single-page applications."
            },
            {
                "question_text": "Which CSS property is used to make text bold?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "text-weight", "is_correct": False},
                    {"text": "font-weight", "is_correct": True},
                    {"text": "text-style", "is_correct": False},
                    {"text": "bold", "is_correct": False}
                ],
                "points": 1,
                "explanation": "The font-weight property is used to set the thickness/boldness of text in CSS."
            },
            {
                "question_text": "What is the purpose of the <script> tag in HTML?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "To link external CSS files", "is_correct": False},
                    {"text": "To embed or reference JavaScript code", "is_correct": True},
                    {"text": "To create a script element", "is_correct": False},
                    {"text": "To add metadata", "is_correct": False}
                ],
                "points": 1,
                "explanation": "The <script> tag is used to embed or reference JavaScript code in an HTML document."
            }
        ]
        
        # Create questions and options
        for i, q_data in enumerate(questions_data):
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                points=q_data["points"],
                order_index=i + 1,
                explanation=q_data.get("explanation")
            )
            db.add(question)
            db.flush()  # Get the question ID
            
            # Create options for this question
            for j, option_data in enumerate(q_data["options"]):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=option_data["text"],
                    is_correct=option_data["is_correct"],
                    order_index=j + 1
                )
                db.add(option)
            
            print(f"  ✅ Created question {i + 1}: {q_data['question_text'][:50]}...")
        
        db.commit()
        print(f"\n✅ Successfully created quiz with {len(questions_data)} questions!")
        
        # Create another quiz for a different difficulty level
        quiz_level2 = Quiz(
            title="Frontend Development Intermediate - Level 2",
            description="Intermediate frontend concepts including React, state management, and advanced CSS",
            specialization_id=frontend_spec.id,
            difficulty_level=2,
            time_limit_minutes=45,
            passing_score=75.0
        )
        db.add(quiz_level2)
        db.commit()
        db.refresh(quiz_level2)
        print(f"✅ Created quiz: {quiz_level2.title} (ID: {quiz_level2.id})")
        
        # Intermediate questions
        intermediate_questions = [
            {
                "question_text": "What is a React Hook?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "A way to connect to external APIs", "is_correct": False},
                    {"text": "A function that lets you use state and lifecycle features", "is_correct": True},
                    {"text": "A CSS styling technique", "is_correct": False},
                    {"text": "A database query method", "is_correct": False}
                ],
                "points": 2,
                "explanation": "React Hooks are functions that let you use state and other React features in functional components."
            },
            {
                "question_text": "What is CSS Grid primarily used for?",
                "question_type": "multiple_choice",
                "options": [
                    {"text": "Animating elements", "is_correct": False},
                    {"text": "Creating two-dimensional layouts", "is_correct": True},
                    {"text": "Styling text", "is_correct": False},
                    {"text": "Adding colors", "is_correct": False}
                ],
                "points": 2,
                "explanation": "CSS Grid is a layout system designed for creating two-dimensional layouts with rows and columns."
            }
        ]
        
        for i, q_data in enumerate(intermediate_questions):
            question = Question(
                quiz_id=quiz_level2.id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                points=q_data["points"],
                order_index=i + 1,
                explanation=q_data.get("explanation")
            )
            db.add(question)
            db.flush()
            
            for j, option_data in enumerate(q_data["options"]):
                option = QuestionOption(
                    question_id=question.id,
                    option_text=option_data["text"],
                    is_correct=option_data["is_correct"],
                    order_index=j + 1
                )
                db.add(option)
        
        db.commit()
        print(f"✅ Created intermediate quiz with {len(intermediate_questions)} questions!")
        
        # Summary
        total_quizzes = db.query(Quiz).filter(Quiz.specialization_id == frontend_spec.id).count()
        total_questions = db.query(Question).join(Quiz).filter(Quiz.specialization_id == frontend_spec.id).count()
        print(f"\n📊 Summary:")
        print(f"   - Quizzes created: {total_quizzes}")
        print(f"   - Total questions: {total_questions}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_quizzes()

