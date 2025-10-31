"""
Temporary in-memory storage
This replaces the database for now
"""

# Store users
users = [
    {
        "id": 1,
        "email": "demo@test.com",
        "password": "password123",
        "name": "Demo User",
        "industry": {
            "industry": "technology",
            "branch": "web-development",
            "specialization": "frontend"
        },
        "readiness_score": 65,
        "technical_score": 70,
        "soft_skills_score": 60,
        "leadership_score": 65
    }
]

# Store quizzes
quizzes = [
    {
        "id": 1,
        "title": "Python Fundamentals",
        "description": "Test your basic Python knowledge",
        "industry": "technology",
        "branch": "web-development",
        "specialization": "backend",
        "duration": "20 mins",
        "question_count": 15,
        "difficulty": "Beginner",
        "questions": [
            {
                "id": 1,
                "question": "What is a variable in Python?",
                "options": [
                    {"id": "A", "text": "A container for storing data"},
                    {"id": "B", "text": "A type of loop"},
                    {"id": "C", "text": "A function"},
                    {"id": "D", "text": "A class"}
                ],
                "correct_answer": "A"
            },
            {
                "id": 2,
                "question": "Which symbol is used for comments in Python?",
                "options": [
                    {"id": "A", "text": "//"},
                    {"id": "B", "text": "#"},
                    {"id": "C", "text": "/* */"},
                    {"id": "D", "text": "<!-- -->"}
                ],
                "correct_answer": "B"
            }
        ]
    },
    {
        "id": 2,
        "title": "JavaScript Basics",
        "description": "Essential JavaScript concepts",
        "industry": "technology",
        "branch": "web-development",
        "specialization": "frontend",
        "duration": "25 mins",
        "question_count": 20,
        "difficulty": "Beginner",
        "questions": [
            {
                "id": 1,
                "question": "What does 'let' keyword do in JavaScript?",
                "options": [
                    {"id": "A", "text": "Declares a constant"},
                    {"id": "B", "text": "Declares a variable"},
                    {"id": "C", "text": "Declares a function"},
                    {"id": "D", "text": "Declares a class"}
                ],
                "correct_answer": "B"
            }
        ]
    }
]

# Store quiz attempts
quiz_attempts = []

# Helper functions
def get_user_by_email(email: str):
    for user in users:
        if user["email"] == email:
            return user
    return None

def get_user_by_id(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def create_user(email: str, password: str, name: str):
    new_id = len(users) + 1
    new_user = {
        "id": new_id,
        "email": email,
        "password": password,
        "name": name,
        "industry": None,
        "readiness_score": 0,
        "technical_score": 0,
        "soft_skills_score": 0,
        "leadership_score": 0
    }
    users.append(new_user)
    return new_user

def update_user_industry(user_id: int, industry_data: dict):
    user = get_user_by_id(user_id)
    if user:
        user["industry"] = industry_data
        return user
    return None

def get_all_quizzes():
    return quizzes

def get_quiz_by_id(quiz_id: int):
    for quiz in quizzes:
        if quiz["id"] == quiz_id:
            return quiz
    return None

def create_quiz_attempt(user_id: int, quiz_id: int):
    attempt_id = len(quiz_attempts) + 1
    attempt = {
        "id": attempt_id,
        "user_id": user_id,
        "quiz_id": quiz_id,
        "answers": [],
        "score": None,
        "completed": False
    }
    quiz_attempts.append(attempt)
    return attempt

def submit_quiz_attempt(attempt_id: int, answers: list):
    attempt = None
    for a in quiz_attempts:
        if a["id"] == attempt_id:
            attempt = a
            break
    
    if not attempt:
        return None
    
    quiz = get_quiz_by_id(attempt["quiz_id"])
    if not quiz:
        return None
    
    correct = 0
    total = len(quiz["questions"])
    
    for answer in answers:
        question_id = answer["question_id"]
        selected = answer["selected_answer"]
        
        for question in quiz["questions"]:
            if question["id"] == question_id:
                if question["correct_answer"] == selected:
                    correct += 1
                break
    
    score = (correct / total * 100) if total > 0 else 0
    
    attempt["answers"] = answers
    attempt["score"] = score
    attempt["completed"] = True
    
    return {
        "score": score,
        "correct": correct,
        "total": total,
        "passed": score >= 70
    }