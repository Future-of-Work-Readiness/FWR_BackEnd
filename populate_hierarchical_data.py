"""
Populate database with hierarchical structure: Technology sector with branches and specializations
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models_hierarchical import Base, Sector, Branch, Specialization

# Create all tables
Base.metadata.create_all(bind=engine)

def populate_technology_sector():
    db = SessionLocal()
    try:
        # Check if Technology sector already exists
        tech_sector = db.query(Sector).filter(Sector.name == "Technology").first()
        
        if tech_sector is None:
            # Create Technology sector if it doesn't exist
            tech_sector = Sector(
                name="Technology",
                description="Comprehensive technology sector covering software development, data science, cybersecurity, infrastructure, and digital innovation."
            )
            db.add(tech_sector)
            db.commit()
            db.refresh(tech_sector)
            print("Created Technology sector")
        else:
            print("Technology sector already exists, using existing one")
        
        # Technology branches and their specializations
        tech_branches = {
            "Software Development & Engineering": {
                "description": "Core of building applications and systems",
                "specializations": [
                    {
                        "name": "Frontend Development",
                        "description": "Focuses on the user interface (UI) and user experience (UX) of a website or app (what the user sees and interacts with)."
                    },
                    {
                        "name": "Backend Development", 
                        "description": "Focuses on the server, database, and application logic that power the frontend (what the user doesn't see)."
                    },
                    {
                        "name": "Full-Stack Development",
                        "description": "A hybrid role that handles both frontend and backend tasks."
                    },
                    {
                        "name": "Mobile Development",
                        "description": "Specializes in building applications for mobile devices (e.g., iOS Developer, Android Developer)."
                    },
                    {
                        "name": "Game Development",
                        "description": "Focuses on building video games, including graphics, physics, and game logic."
                    },
                    {
                        "name": "Software Engineering in Test (SET) / QA Automation",
                        "description": "Writes code specifically to test other software and build automated testing systems."
                    }
                ]
            },
            "Data & Artificial Intelligence": {
                "description": "Focused on managing, interpreting, and leveraging data",
                "specializations": [
                    {
                        "name": "Data Analytics",
                        "description": "Focuses on interpreting historical data to find trends and answer business questions (What happened? Why?)."
                    },
                    {
                        "name": "Data Science",
                        "description": "Uses statistics, machine learning, and programming to make predictions and build models (What will happen?)."
                    },
                    {
                        "name": "Data Engineering",
                        "description": "Builds and maintains the 'pipelines' and infrastructure that collect, store, and prepare large volumes of data for analysis."
                    },
                    {
                        "name": "AI / Machine Learning Engineering",
                        "description": "Specializes in designing and building complex artificial intelligence and predictive models."
                    },
                    {
                        "name": "Database Administration (DBA)",
                        "description": "Manages, secures, and maintains the health and performance of a company's databases."
                    }
                ]
            },
            "Cybersecurity": {
                "description": "Dedicated to protecting data, networks, and systems from threats",
                "specializations": [
                    {
                        "name": "Cybersecurity Analyst / InfoSec Analyst",
                        "description": "The front line of defense; monitors networks, investigates alerts, and responds to security incidents."
                    },
                    {
                        "name": "Penetration Tester / Ethical Hacker",
                        "description": "Paid to legally hack into systems to find vulnerabilities before malicious actors do."
                    },
                    {
                        "name": "Security Engineering",
                        "description": "Designs and builds secure network and system architectures."
                    },
                    {
                        "name": "Governance, Risk & Compliance (GRC)",
                        "description": "Focuses on policy, law, and standards (like GDPR, HIPAA, ISO 27001) to ensure the company is following security rules."
                    }
                ]
            },
            "IT Infrastructure & Cloud": {
                "description": "The backbone that supports all other technology functions",
                "specializations": [
                    {
                        "name": "Cloud Engineering",
                        "description": "Manages and builds infrastructure on cloud platforms like Amazon Web Services (AWS), Microsoft Azure, or Google Cloud (GCP)."
                    },
                    {
                        "name": "DevOps Engineering",
                        "description": "Bridges the gap between Software Development (Dev) and IT Operations (Ops), focusing on automation, deployment, and efficiency (CI/CD)."
                    },
                    {
                        "name": "Network Engineering / Administration",
                        "description": "Manages the internal and external networks (Wi-Fi, routers, switches, LAN/WAN) that allow computers to communicate."
                    },
                    {
                        "name": "Systems Administration",
                        "description": "Manages the company's servers, operating systems (like Linux or Windows Server), and core IT functions."
                    },
                    {
                        "name": "IT Support / Help Desk",
                        "description": "Provides direct technical support to employees, troubleshooting hardware, software, and access issues."
                    }
                ]
            },
            "Product & Project Management": {
                "description": "Organize the work and define the why and what to build",
                "specializations": [
                    {
                        "name": "Technical Project Manager",
                        "description": "Organizes the timeline, resources, and budget to ensure a technology project is completed on time."
                    },
                    {
                        "name": "Product Manager",
                        "description": "Decides what gets built. They represent the customer, define product features, and align the technology with business goals."
                    },
                    {
                        "name": "Scrum Master / Agile Coach",
                        "description": "A specific role that facilitates the Agile development process, removes obstacles, and coaches the team."
                    },
                    {
                        "name": "Business Analyst (Technical)",
                        "description": "Works as a liaison between business stakeholders and the tech team to translate business needs into technical requirements."
                    }
                ]
            },
            "Design & User Experience": {
                "description": "Focuses on the human side of technology",
                "specializations": [
                    {
                        "name": "UX Designer (User Experience)",
                        "description": "Researches user behavior to design a product that is logical, intuitive, and easy to use."
                    },
                    {
                        "name": "UI Designer (User Interface)",
                        "description": "Focuses on the visual elements of a product (buttons, colors, typography, layout) to make it beautiful and functional."
                    },
                    {
                        "name": "UX Researcher",
                        "description": "Conducts interviews, surveys, and usability tests to understand user needs and pain points."
                    }
                ]
            }
        }
        
        # Create branches and specializations
        for branch_name, branch_data in tech_branches.items():
            # Check if branch already exists
            branch = db.query(Branch).filter(
                Branch.name == branch_name,
                Branch.sector_id == tech_sector.id
            ).first()
            
            if branch is None:
                # Create branch if it doesn't exist
                branch = Branch(
                    name=branch_name,
                    description=branch_data["description"],
                    sector_id=tech_sector.id
                )
                db.add(branch)
                db.commit()
                db.refresh(branch)
                print(f"Created branch: {branch_name}")
            else:
                print(f"Branch '{branch_name}' already exists, using existing one")
            
            # Create specializations for this branch
            for spec_data in branch_data["specializations"]:
                # Check if specialization already exists
                existing_spec = db.query(Specialization).filter(
                    Specialization.name == spec_data["name"],
                    Specialization.branch_id == branch.id
                ).first()
                
                if existing_spec is None:
                    specialization = Specialization(
                        name=spec_data["name"],
                        description=spec_data["description"],
                        branch_id=branch.id
                    )
                    db.add(specialization)
                    print(f"  - Added specialization: {spec_data['name']}")
                else:
                    print(f"  - Specialization '{spec_data['name']}' already exists")
            
            db.commit()
        
        print(f"\n✅ Successfully populated Technology sector with {len(tech_branches)} branches and their specializations!")
        
        # Print summary
        total_specializations = sum(len(branch_data["specializations"]) for branch_data in tech_branches.values())
        print(f"📊 Summary:")
        print(f"   - 1 Sector: Technology")
        print(f"   - {len(tech_branches)} Branches")
        print(f"   - {total_specializations} Specializations")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_technology_sector()
