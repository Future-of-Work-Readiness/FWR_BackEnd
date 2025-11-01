#!/usr/bin/env python3
"""
SQLAlchemy ORM Examples - Learn how to interact with database using ORM
This file contains practical examples of common database operations
"""

from app.database import SessionLocal
from app.models_hierarchical import (
    Sector, Branch, Specialization, Quiz, Question, QuestionOption, User, QuizAttempt
)
from datetime import datetime, timezone

# Get database session
db = SessionLocal()

# ============================================================
# 1. CREATE (INSERT) OPERATIONS
# ============================================================

def example_create_sector():
    """Create a new sector"""
    new_sector = Sector(
        name="Technology",
        description="Technology and IT sector"
    )
    db.add(new_sector)
    db.commit()
    db.refresh(new_sector)  # Refresh to get auto-generated ID
    print(f"Created sector: {new_sector.id} - {new_sector.name}")
    return new_sector

def example_create_branch(sector_id):
    """Create a new branch under a sector"""
    new_branch = Branch(
        name="Software Development",
        description="Software development and engineering",
        sector_id=sector_id
    )
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    print(f"Created branch: {new_branch.id} - {new_branch.name}")
    return new_branch

def example_create_user():
    """Create a new user"""
    new_user = User(
        name="John Doe",
        email="john@example.com",
        password_hash="hashed_password_here"  # In production, use bcrypt!
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"Created user: {new_user.id} - {new_user.email}")
    return new_user

# ============================================================
# 2. READ (SELECT) OPERATIONS
# ============================================================

def example_get_all_sectors():
    """Get all sectors"""
    sectors = db.query(Sector).filter(Sector.is_active == True).all()
    for sector in sectors:
        print(f"Sector: {sector.name} (ID: {sector.id})")
    return sectors

def example_get_sector_by_id(sector_id):
    """Get a sector by ID"""
    sector = db.query(Sector).filter(Sector.id == sector_id).first()
    if sector:
        print(f"Found: {sector.name}")
    else:
        print("Sector not found")
    return sector

def example_get_sectors_with_branches():
    """Get sectors with their branches (using relationships)"""
    sectors = db.query(Sector).filter(Sector.is_active == True).all()
    for sector in sectors:
        print(f"\nSector: {sector.name}")
        for branch in sector.branches:
            print(f"  - Branch: {branch.name}")

def example_filter_example():
    """Examples of filtering"""
    # Get all active users
    active_users = db.query(User).filter(User.is_active == True).all()
    
    # Get user by email
    user = db.query(User).filter(User.email == "john@example.com").first()
    
    # Get users with score > 70
    high_scores = db.query(User).filter(User.readiness_score > 70.0).all()
    
    # Multiple conditions
    users = db.query(User).filter(
        User.is_active == True,
        User.readiness_score > 50.0
    ).all()
    
    # Using like for search
    search_results = db.query(Sector).filter(
        Sector.name.like("%Tech%")
    ).all()

def example_count_example():
    """Count records"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    print(f"Total users: {total_users}, Active: {active_users}")

# ============================================================
# 3. UPDATE OPERATIONS
# ============================================================

def example_update_user(user_id):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = "Updated Name"
        user.readiness_score = 85.5
        user.preferred_specialization_id = 1
        db.commit()
        db.refresh(user)
        print(f"Updated user: {user.name}")
    return user

def example_bulk_update():
    """Update multiple records"""
    # Update all users' readiness_score
    db.query(User).filter(User.readiness_score < 50).update({
        User.readiness_score: 50.0
    })
    db.commit()

# ============================================================
# 4. DELETE OPERATIONS
# ============================================================

def example_delete_user(user_id):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        print(f"Deleted user: {user.email}")

def example_soft_delete():
    """Soft delete (mark as inactive)"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        print(f"Deactivated user: {user.email}")

# ============================================================
# 5. RELATIONSHIPS AND JOINS
# ============================================================

def example_get_user_with_specialization(user_id):
    """Get user with their specialization"""
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.preferred_specialization:
        print(f"User: {user.name}")
        print(f"Specialization: {user.preferred_specialization.name}")
        # Navigate further
        branch = user.preferred_specialization.branch
        sector = branch.sector
        print(f"Branch: {branch.name}, Sector: {sector.name}")

def example_get_quiz_with_questions(quiz_id):
    """Get quiz with all questions and options"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz:
        print(f"Quiz: {quiz.title}")
        for question in quiz.questions:
            print(f"  Question: {question.question_text}")
            for option in question.options:
                mark = "✓" if option.is_correct else " "
                print(f"    {mark} {option.option_text}")

# ============================================================
# 6. AGGREGATIONS AND ORDERING
# ============================================================

def example_order_by():
    """Order results"""
    # Order by score descending
    top_users = db.query(User).order_by(User.readiness_score.desc()).limit(10).all()
    
    # Order by multiple fields
    sectors = db.query(Sector).order_by(
        Sector.is_active.desc(),
        Sector.name.asc()
    ).all()

def example_aggregations():
    """Aggregate functions"""
    from sqlalchemy import func
    
    # Average score
    avg_score = db.query(func.avg(User.readiness_score)).scalar()
    print(f"Average readiness score: {avg_score}")
    
    # Max score
    max_score = db.query(func.max(User.readiness_score)).scalar()
    
    # Count by specialization
    results = db.query(
        Specialization.name,
        func.count(User.id)
    ).join(
        User, User.preferred_specialization_id == Specialization.id
    ).group_by(Specialization.name).all()
    
    for spec_name, user_count in results:
        print(f"{spec_name}: {user_count} users")

# ============================================================
# 7. TRANSACTIONS AND ERROR HANDLING
# ============================================================

def example_transaction():
    """Example of transaction"""
    try:
        # Create multiple related records
        sector = Sector(name="New Sector")
        db.add(sector)
        db.flush()  # Get ID without committing
        
        branch = Branch(name="New Branch", sector_id=sector.id)
        db.add(branch)
        
        db.commit()  # Commit all changes
        print("Transaction successful!")
    except Exception as e:
        db.rollback()  # Rollback on error
        print(f"Error: {e}")

# ============================================================
# 8. QUERY EXAMPLES WITH CONDITIONS
# ============================================================

def example_complex_queries():
    """Complex query examples"""
    from sqlalchemy import and_, or_
    
    # Multiple AND conditions
    users = db.query(User).filter(
        and_(
            User.is_active == True,
            User.readiness_score > 70,
            User.technical_score > 60
        )
    ).all()
    
    # OR conditions
    sectors = db.query(Sector).filter(
        or_(
            Sector.name == "Technology",
            Sector.name == "Healthcare"
        )
    ).all()
    
    # IN clause
    user_ids = [1, 2, 3, 4, 5]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    
    # Between
    users = db.query(User).filter(
        User.readiness_score.between(50, 100)
    ).all()

# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("SQLAlchemy ORM Examples")
    print("=" * 60)
    
    # Uncomment to run examples:
    
    # example_get_all_sectors()
    # example_get_sectors_with_branches()
    # example_count_example()
    
    # Clean up
    db.close()

