#!/usr/bin/env python3
"""
Database Manager - Interactive tool to access and manage database using SQLAlchemy ORM
Usage: python db_manager.py
"""

import sys
from app.database import SessionLocal, engine
from app.models_hierarchical import (
    Sector, Branch, Specialization, Quiz, Question, QuestionOption, User, QuizAttempt
)
from sqlalchemy import inspect
from datetime import datetime, timezone

def print_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("📊 DATABASE MANAGER - SQLAlchemy ORM Interface")
    print("="*60)
    print("1. List all sectors")
    print("2. List all branches")
    print("3. List all specializations")
    print("4. List all quizzes")
    print("5. List all users")
    print("6. Create new sector")
    print("7. Create new branch")
    print("8. Create new specialization")
    print("9. Create new user")
    print("10. Update user")
    print("11. Delete record")
    print("12. View database schema")
    print("13. Show statistics")
    print("0. Exit")
    print("="*60)

def list_sectors(db):
    """List all sectors"""
    sectors = db.query(Sector).filter(Sector.is_active == True).all()
    if not sectors:
        print("No sectors found.")
        return
    
    print(f"\n📋 Found {len(sectors)} sectors:")
    print("-" * 60)
    for sector in sectors:
        print(f"ID: {sector.id} | Name: {sector.name}")
        if sector.description:
            print(f"     Description: {sector.description[:50]}...")
        branches_count = db.query(Branch).filter(Branch.sector_id == sector.id).count()
        print(f"     Branches: {branches_count}")

def list_branches(db):
    """List all branches"""
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    if not branches:
        print("No branches found.")
        return
    
    print(f"\n📋 Found {len(branches)} branches:")
    print("-" * 60)
    for branch in branches:
        sector = db.query(Sector).filter(Sector.id == branch.sector_id).first()
        print(f"ID: {branch.id} | Name: {branch.name}")
        print(f"     Sector: {sector.name if sector else 'Unknown'} (ID: {branch.sector_id})")
        specs_count = db.query(Specialization).filter(Specialization.branch_id == branch.id).count()
        print(f"     Specializations: {specs_count}")

def list_specializations(db):
    """List all specializations"""
    specializations = db.query(Specialization).filter(Specialization.is_active == True).all()
    if not specializations:
        print("No specializations found.")
        return
    
    print(f"\n📋 Found {len(specializations)} specializations:")
    print("-" * 60)
    for spec in specializations:
        branch = db.query(Branch).filter(Branch.id == spec.branch_id).first()
        sector = db.query(Sector).filter(Sector.id == branch.sector_id).first() if branch else None
        print(f"ID: {spec.id} | Name: {spec.name}")
        print(f"     Branch: {branch.name if branch else 'Unknown'} | Sector: {sector.name if sector else 'Unknown'}")
        quizzes_count = db.query(Quiz).filter(Quiz.specialization_id == spec.id).count()
        print(f"     Quizzes: {quizzes_count}")

def list_quizzes(db):
    """List all quizzes"""
    quizzes = db.query(Quiz).filter(Quiz.is_active == True).all()
    if not quizzes:
        print("No quizzes found.")
        return
    
    print(f"\n📋 Found {len(quizzes)} quizzes:")
    print("-" * 60)
    for quiz in quizzes:
        spec = db.query(Specialization).filter(Specialization.id == quiz.specialization_id).first()
        questions_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
        print(f"ID: {quiz.id} | Title: {quiz.title}")
        print(f"     Specialization: {spec.name if spec else 'Unknown'}")
        print(f"     Difficulty: {quiz.difficulty_level} | Duration: {quiz.time_limit_minutes} min")
        print(f"     Questions: {questions_count}")

def list_users(db):
    """List all users"""
    users = db.query(User).filter(User.is_active == True).all()
    if not users:
        print("No users found.")
        return
    
    print(f"\n📋 Found {len(users)} users:")
    print("-" * 60)
    for user in users:
        spec = None
        if user.preferred_specialization_id:
            spec = db.query(Specialization).filter(Specialization.id == user.preferred_specialization_id).first()
        print(f"ID: {user.id} | Name: {user.name} | Email: {user.email}")
        print(f"     Specialization: {spec.name if spec else 'None'}")
        print(f"     Scores - Readiness: {user.readiness_score}, Technical: {user.technical_score}")
        attempts_count = db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id).count()
        print(f"     Quiz Attempts: {attempts_count}")

def create_sector(db):
    """Create a new sector"""
    print("\n➕ Create New Sector")
    name = input("Sector name: ").strip()
    if not name:
        print("❌ Name is required!")
        return
    
    description = input("Description (optional): ").strip()
    
    # Check if sector already exists
    existing = db.query(Sector).filter(Sector.name == name).first()
    if existing:
        print(f"❌ Sector '{name}' already exists (ID: {existing.id})")
        return
    
    sector = Sector(name=name, description=description if description else None)
    db.add(sector)
    db.commit()
    db.refresh(sector)
    print(f"✅ Sector created successfully! ID: {sector.id}")

def create_branch(db):
    """Create a new branch"""
    print("\n➕ Create New Branch")
    
    # List sectors first
    sectors = db.query(Sector).filter(Sector.is_active == True).all()
    if not sectors:
        print("❌ No sectors found. Please create a sector first.")
        return
    
    print("Available sectors:")
    for sector in sectors:
        print(f"  {sector.id}. {sector.name}")
    
    try:
        sector_id = int(input("\nSelect sector ID: "))
        sector = db.query(Sector).filter(Sector.id == sector_id).first()
        if not sector:
            print("❌ Invalid sector ID!")
            return
    except ValueError:
        print("❌ Invalid input!")
        return
    
    name = input("Branch name: ").strip()
    if not name:
        print("❌ Name is required!")
        return
    
    description = input("Description (optional): ").strip()
    
    branch = Branch(name=name, description=description if description else None, sector_id=sector_id)
    db.add(branch)
    db.commit()
    db.refresh(branch)
    print(f"✅ Branch created successfully! ID: {branch.id}")

def create_specialization(db):
    """Create a new specialization"""
    print("\n➕ Create New Specialization")
    
    # List branches first
    branches = db.query(Branch).filter(Branch.is_active == True).all()
    if not branches:
        print("❌ No branches found. Please create a branch first.")
        return
    
    print("Available branches:")
    for branch in branches:
        sector = db.query(Sector).filter(Sector.id == branch.sector_id).first()
        print(f"  {branch.id}. {branch.name} (Sector: {sector.name if sector else 'Unknown'})")
    
    try:
        branch_id = int(input("\nSelect branch ID: "))
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch:
            print("❌ Invalid branch ID!")
            return
    except ValueError:
        print("❌ Invalid input!")
        return
    
    name = input("Specialization name: ").strip()
    if not name:
        print("❌ Name is required!")
        return
    
    description = input("Description (optional): ").strip()
    
    specialization = Specialization(
        name=name, 
        description=description if description else None, 
        branch_id=branch_id
    )
    db.add(specialization)
    db.commit()
    db.refresh(specialization)
    print(f"✅ Specialization created successfully! ID: {specialization.id}")

def create_user(db):
    """Create a new user"""
    print("\n➕ Create New User")
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    if not name or not email or not password:
        print("❌ All fields are required!")
        return
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        print(f"❌ User with email '{email}' already exists (ID: {existing.id})")
        return
    
    user = User(name=name, email=email, password_hash=password)  # In production, hash this!
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ User created successfully! ID: {user.id}")

def update_user(db):
    """Update user information"""
    print("\n✏️  Update User")
    try:
        user_id = int(input("User ID: "))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print("❌ User not found!")
            return
        
        print(f"\nCurrent user: {user.name} ({user.email})")
        print("\nWhat would you like to update?")
        print("1. Name")
        print("2. Email")
        print("3. Specialization")
        print("4. Scores")
        
        choice = input("Choice: ").strip()
        
        if choice == "1":
            new_name = input("New name: ").strip()
            if new_name:
                user.name = new_name
        elif choice == "2":
            new_email = input("New email: ").strip()
            if new_email:
                user.email = new_email
        elif choice == "3":
            specs = db.query(Specialization).filter(Specialization.is_active == True).all()
            if specs:
                print("Available specializations:")
                for spec in specs:
                    print(f"  {spec.id}. {spec.name}")
                spec_id = input("Specialization ID (press Enter to clear): ").strip()
                user.preferred_specialization_id = int(spec_id) if spec_id else None
        elif choice == "4":
            user.readiness_score = float(input("Readiness score: ") or "0")
            user.technical_score = float(input("Technical score: ") or "0")
            user.soft_skills_score = float(input("Soft skills score: ") or "0")
        
        db.commit()
        print("✅ User updated successfully!")
    except ValueError:
        print("❌ Invalid input!")
    except Exception as e:
        print(f"❌ Error: {e}")

def delete_record(db):
    """Delete a record"""
    print("\n🗑️  Delete Record")
    print("1. Sector")
    print("2. Branch")
    print("3. Specialization")
    print("4. User")
    
    choice = input("What to delete: ").strip()
    
    try:
        record_id = int(input("Record ID: "))
        
        if choice == "1":
            record = db.query(Sector).filter(Sector.id == record_id).first()
        elif choice == "2":
            record = db.query(Branch).filter(Branch.id == record_id).first()
        elif choice == "3":
            record = db.query(Specialization).filter(Specialization.id == record_id).first()
        elif choice == "4":
            record = db.query(User).filter(User.id == record_id).first()
        else:
            print("❌ Invalid choice!")
            return
        
        if not record:
            print("❌ Record not found!")
            return
        
        confirm = input(f"Are you sure you want to delete? (yes/no): ").strip().lower()
        if confirm == "yes":
            db.delete(record)
            db.commit()
            print("✅ Record deleted successfully!")
        else:
            print("❌ Deletion cancelled.")
    except ValueError:
        print("❌ Invalid input!")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_schema(db):
    """Show database schema"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n📐 Database Schema:")
    print("-" * 60)
    for table_name in tables:
        print(f"\n📋 Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for col in columns:
            print(f"   - {col['name']}: {col['type']}")

def show_statistics(db):
    """Show database statistics"""
    print("\n📊 Database Statistics:")
    print("-" * 60)
    print(f"Sectors: {db.query(Sector).count()}")
    print(f"Branches: {db.query(Branch).count()}")
    print(f"Specializations: {db.query(Specialization).count()}")
    print(f"Quizzes: {db.query(Quiz).count()}")
    print(f"Questions: {db.query(Question).count()}")
    print(f"Users: {db.query(User).count()}")
    print(f"Quiz Attempts: {db.query(QuizAttempt).count()}")

def main():
    """Main function"""
    db = SessionLocal()
    
    try:
        while True:
            print_menu()
            choice = input("\nSelect an option: ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                list_sectors(db)
            elif choice == "2":
                list_branches(db)
            elif choice == "3":
                list_specializations(db)
            elif choice == "4":
                list_quizzes(db)
            elif choice == "5":
                list_users(db)
            elif choice == "6":
                create_sector(db)
            elif choice == "7":
                create_branch(db)
            elif choice == "8":
                create_specialization(db)
            elif choice == "9":
                create_user(db)
            elif choice == "10":
                update_user(db)
            elif choice == "11":
                delete_record(db)
            elif choice == "12":
                show_schema(db)
            elif choice == "13":
                show_statistics(db)
            else:
                print("❌ Invalid option!")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

