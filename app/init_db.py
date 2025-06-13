import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Base, DATABASE_URL
from models import User, Project, Task, Comment, UserRole, TaskStatus, TaskPriority
from auth import get_password_hash

def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    return engine

def create_sample_data(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("⚠️  Sample data already exists. Skipping...")
            return
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.admin
        )
        
        user1 = User(
            username="john_doe",
            email="john@example.com",
            hashed_password=get_password_hash("user123"),
            role=UserRole.user
        )
        
        user2 = User(
            username="jane_smith",
            email="jane@example.com",
            hashed_password=get_password_hash("user123"),
            role=UserRole.user
        )
        
        db.add(admin_user)
        db.add(user1)
        db.add(user2)
        db.commit()
        
        db.refresh(admin_user)
        db.refresh(user1)
        db.refresh(user2)
        
        project1 = Project(
            title="Website Redesign",
            description="Complete redesign of company website with modern UI/UX",
            creator_id=admin_user.id
        )
        
        project2 = Project(
            title="Mobile App Development",
            description="Develop mobile application for iOS and Android",
            creator_id=admin_user.id
        )
        
        db.add(project1)
        db.add(project2)
        db.commit()

        db.refresh(project1)
        db.refresh(project2)
        
        tasks = [
            Task(
                title="Design Homepage Mockup",
                description="Create modern homepage design with responsive layout",
                project_id=project1.id,
                assignee_id=user1.id,
                deadline=datetime.now() + timedelta(days=7),
                priority=TaskPriority.high,
                status=TaskStatus.in_progress
            ),
            Task(
                title="Implement User Authentication",
                description="Set up secure user login and registration system",
                project_id=project1.id,
                assignee_id=user2.id,
                deadline=datetime.now() + timedelta(days=10),
                priority=TaskPriority.medium,
                status=TaskStatus.pending
            ),
            Task(
                title="Mobile App UI Design",
                description="Design mobile app user interface screens",
                project_id=project2.id,
                assignee_id=user1.id,
                deadline=datetime.now() + timedelta(days=14),
                priority=TaskPriority.medium,
                status=TaskStatus.pending
            ),
            Task(
                title="Database Schema Design",
                description="Design database structure for mobile app",
                project_id=project2.id,
                assignee_id=user2.id,
                deadline=datetime.now() + timedelta(days=5),
                priority=TaskPriority.high,
                status=TaskStatus.completed
            )
        ]
        
        for task in tasks:
            db.add(task)
        
        db.commit()
        
        for task in tasks:
            db.refresh(task)
        
        comments = [
            Comment(
                content="Started working on the mockup. Will have initial draft ready by tomorrow.",
                task_id=tasks[0].id,
                author_id=user1.id
            ),
            Comment(
                content="Please use the brand colors specified in the style guide.",
                task_id=tasks[0].id,
                author_id=admin_user.id
            ),
            Comment(
                content="Database schema has been finalized and approved.",
                task_id=tasks[3].id,
                author_id=user2.id
            )
        ]
        
        for comment in comments:
            db.add(comment)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print("\n📋 Sample Login Credentials:")
        print("Admin User:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: admin")
        print("\nRegular Users:")
        print("  Username: john_doe | Password: user123")
        print("  Username: jane_smith | Password: user123")
        print("  Role: user")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🚀 Initializing Team Task Management Database...")
    print(f"📍 Database URL: {DATABASE_URL}")
    
    try:
        engine = create_tables()

        create_sample = input("\n❓ Do you want to create sample data for testing? (y/n): ").lower().strip()
        
        if create_sample in ['y', 'yes']:
            create_sample_data(engine)
        else:
            print("✅ Database initialized without sample data.")
        
        print("\n🎉 Database initialization completed!")
        print("\n🔧 Next steps:")
        print("1. Start the backend server: python main.py")
        print("2. Start the frontend: streamlit run ../frontend/streamlit_app.py")
        print("3. Open http://localhost:8501 in your browser")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("\n🔍 Common issues:")
        print("- Make sure PostgreSQL is running")
        print("- Check your DATABASE_URL in .env file")
        print("- Ensure the database and user exist")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())