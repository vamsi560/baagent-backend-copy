# database_multi_user.py
# Multi-User and Project Management Database Schema

import os
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, JSON, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime
import uuid
import hashlib
from enum import Enum

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://bauser:Valuemomentum123@baagent.postgres.database.azure.com:5432/ba_agent')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    APPROVER = "approver"
    VIEWER = "viewer"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    COMPLETED = "completed"

class ProjectUserRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"
    VIEWER = "viewer"

# Association Tables
user_projects = Table('user_projects', Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('project_id', String, ForeignKey('projects.id'), primary_key=True),
    Column('role', String, default=ProjectUserRole.MEMBER),
    Column('joined_at', DateTime, default=datetime.utcnow)
)

project_documents = Table('project_documents', Base.metadata,
    Column('project_id', String, ForeignKey('projects.id'), primary_key=True),
    Column('document_id', Integer, ForeignKey('documents.id'), primary_key=True),  # Changed to Integer
    Column('added_at', DateTime, default=datetime.utcnow)
)

project_analyses = Table('project_analyses', Base.metadata,
    Column('project_id', String, ForeignKey('projects.id'), primary_key=True),
    Column('analysis_id', String, ForeignKey('analyses.id'), primary_key=True),
    Column('added_at', DateTime, default=datetime.utcnow)
)

# Core Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default=UserRole.ANALYST)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(JSON)  # User preferences and settings
    
    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    project_memberships = relationship("Project", secondary=user_projects, back_populates="members")
    analyses = relationship("Analysis", back_populates="user")
    text_inputs = relationship("TextInput", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String, default=ProjectStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON)  # Project-specific settings
    ado_project_id = Column(String)  # Azure DevOps project ID
    
    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    members = relationship("User", secondary=user_projects, back_populates="project_memberships")
    documents = relationship("Document", secondary=project_documents, back_populates="projects")
    analyses = relationship("Analysis", secondary=project_analyses, back_populates="projects")
    text_inputs = relationship("TextInput", back_populates="project")

# Enhanced Document Model
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)  # Keep as Integer to match existing schema
    name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    content = Column(Text)
    meta = Column(JSON)
    status = Column(String, default="uploaded")
    file_hash = Column(String, nullable=False)
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    original_document_id = Column(Integer)  # Changed to Integer
    uploaded_by = Column(String, ForeignKey("users.id"))
    file_size = Column(Integer)
    source_type = Column(String)  # 'local', 'ado'
    source_id = Column(String)  # Original file ID from source
    
    # Relationships
    projects = relationship("Project", secondary=project_documents, back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")
    analyses = relationship("Analysis", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(String, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)  # Changed to Integer
    version = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    content = Column(Text)
    file_hash = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String, ForeignKey("users.id"))
    change_summary = Column(Text)
    file_size = Column(Integer)
    
    # Relationships
    document = relationship("Document", back_populates="versions")

# Text Input Model
class TextInput(Base):
    __tablename__ = "text_inputs"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    template_id = Column(String)  # Reference to template used
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    auto_saved = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="text_inputs")
    project = relationship("Project", back_populates="text_inputs")
    analyses = relationship("Analysis", back_populates="text_input")

# Enhanced Analysis Model
class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    original_text = Column(Text)
    results = Column(JSON)
    document_id = Column(Integer, ForeignKey("documents.id"))  # Changed to Integer
    text_input_id = Column(String, ForeignKey("text_inputs.id"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    analysis_type = Column(String)
    quality_score = Column(Integer)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    text_input = relationship("TextInput", back_populates="analyses")
    user = relationship("User", back_populates="analyses")
    projects = relationship("Project", secondary=project_analyses, back_populates="analyses")
    approvals = relationship("Approval", back_populates="analysis")

# Enhanced Approval Model
class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    status = Column(String, default="pending")
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow)
    approver_email = Column(String)
    results_summary = Column(JSON)
    approver_response = Column(Text)
    ado_result = Column(JSON)
    approval_notes = Column(Text)
    approval_date = Column(DateTime)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="approvals")

# Integration Models
class AzureDevOpsIntegration(Base):
    __tablename__ = "ado_integrations"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    organization_url = Column(String, nullable=False)
    project_id = Column(String, nullable=False)
    pat_token_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime)
    sync_settings = Column(JSON)  # What to sync (work items, boards, etc.)

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)

# Database Operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with multi-user schema"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Multi-user database tables created successfully")
    except Exception as e:
        print(f"❌ Error initializing multi-user database: {e}")
        raise e

# User Management Functions
def create_user(db, email: str, name: str, password: str, role: str = UserRole.ANALYST):
    """Create a new user"""
    try:
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = User(
            id=user_id,
            email=email,
            name=name,
            password_hash=password_hash,
            role=role
        )
        db.add(user)
        db.commit()
        print(f"✅ User created: {email}")
        return user
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        raise e

def authenticate_user(db, email: str, password: str):
    """Authenticate user login"""
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = db.query(User).filter(
            User.email == email,
            User.password_hash == password_hash,
            User.is_active == True
        ).first()
        return user
    except Exception as e:
        print(f"❌ Error authenticating user: {e}")
        return None

# Project Management Functions
def create_project(db, name: str, description: str, owner_id: str):
    """Create a new project"""
    try:
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name=name,
            description=description,
            owner_id=owner_id
        )
        db.add(project)
        db.commit()
        print(f"✅ Project created: {name}")
        return project
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating project: {e}")
        raise e

def add_user_to_project(db, user_id: str, project_id: str, role: str = ProjectUserRole.MEMBER):
    """Add user to project"""
    try:
        # Check if user is already in project
        existing = db.execute(
            user_projects.select().where(
                user_projects.c.user_id == user_id,
                user_projects.c.project_id == project_id
            )
        ).first()
        
        if existing:
            print(f"⚠️ User {user_id} already in project {project_id}")
            return False
        
        # Add user to project
        db.execute(
            user_projects.insert().values(
                user_id=user_id,
                project_id=project_id,
                role=role
            )
        )
        db.commit()
        print(f"✅ User {user_id} added to project {project_id}")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding user to project: {e}")
        return False

def get_user_projects(db, user_id: str):
    """Get all projects for a user"""
    try:
        # Get owned projects
        owned_projects = db.query(Project).filter(Project.owner_id == user_id).all()
        
        # Get member projects
        member_projects = db.query(Project).join(user_projects).filter(
            user_projects.c.user_id == user_id
        ).all()
        
        all_projects = list(set(owned_projects + member_projects))
        
        return [
            {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'created_at': project.created_at.isoformat(),
                'owner_id': project.owner_id,
                'is_owner': project.owner_id == user_id
            }
            for project in all_projects
        ]
    except Exception as e:
        print(f"❌ Error getting user projects: {e}")
        return []

# Text Input Functions
def save_text_input(db, title: str, content: str, user_id: str, project_id: str, template_id: str = None):
    """Save text input with versioning"""
    try:
        input_id = str(uuid.uuid4())
        text_input = TextInput(
            id=input_id,
            title=title,
            content=content,
            user_id=user_id,
            project_id=project_id,
            template_id=template_id
        )
        db.add(text_input)
        db.commit()
        print(f"✅ Text input saved: {title}")
        return text_input
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving text input: {e}")
        raise e

# Test function
def test_multi_user_database():
    """Test the multi-user database functionality"""
    print("🧪 Testing Multi-User Database Functionality...")
    
    # Initialize database
    init_db()
    
    # Test user and project creation
    db = next(get_db())
    try:
        # Create test user
        user = create_user(db, "test@example.com", "Test User", "password123")
        print(f"✅ User created: {user.email}")
        
        # Create test project
        project = create_project(db, "Test Project", "A test project", user.id)
        print(f"✅ Project created: {project.name}")
        
        # Add user to project
        success = add_user_to_project(db, user.id, project.id)
        print(f"✅ User added to project: {success}")
        
        # Get user projects
        projects = get_user_projects(db, user.id)
        print(f"✅ User projects: {len(projects)}")
        
        # Save text input
        text_input = save_text_input(db, "Test Requirements", "Sample requirements text", user.id, project.id)
        print(f"✅ Text input saved: {text_input.title}")
        
        return {
            'success': True,
            'user_created': user.id,
            'project_created': project.id,
            'projects_count': len(projects),
            'text_input_created': text_input.id
        }
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    test_multi_user_database()
