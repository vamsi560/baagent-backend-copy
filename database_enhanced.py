# database_enhanced.py
# Enhanced Database with Document Versioning, Storage, and Approval Tracking

import os
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime
import uuid
from io import BytesIO
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://bauser:Valuemomentum123@baagent.postgres.database.azure.com:5432/ba_agent')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enhanced Database Models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    content = Column(Text)
    meta = Column(JSON)
    status = Column(String, default="uploaded")
    file_hash = Column(String, nullable=False)  # For versioning
    version = Column(Integer, default=1)  # Version number
    is_latest = Column(Boolean, default=True)  # Latest version flag
    original_document_id = Column(String)  # Reference to original document for versioning
    uploaded_by = Column(String)  # User who uploaded
    file_size = Column(Integer)  # File size in bytes
    
    # Relationships
    versions = relationship("DocumentVersion", back_populates="document")
    analyses = relationship("Analysis", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    version = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    content = Column(Text)
    file_hash = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String)
    change_summary = Column(Text)  # Summary of changes from previous version
    file_size = Column(Integer)
    
    # Relationships
    document = relationship("Document", back_populates="versions")

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    original_text = Column(Text)
    results = Column(JSON)
    document_id = Column(String, ForeignKey("documents.id"))
    user_email = Column(String)
    analysis_type = Column(String)  # HLD, LLD, Backlog, etc.
    quality_score = Column(Integer)  # Quality score from validation
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    approvals = relationship("Approval", back_populates="analysis")

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected, in_review
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow)
    approver_email = Column(String)
    results_summary = Column(JSON)
    approver_response = Column(Text)
    ado_result = Column(JSON)
    approval_notes = Column(Text)  # Additional notes from approver
    approval_date = Column(DateTime)  # When approval was given/rejected
    
    # Relationships
    analysis = relationship("Analysis", back_populates="approvals")

class VectorEmbedding(Base):
    __tablename__ = "vector_embeddings"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)
    meta = Column(JSON)
    source_type = Column(String)
    source_id = Column(String)

# Database Operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with enhanced models"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Enhanced database tables created successfully")
    except Exception as e:
        print(f"❌ Error initializing enhanced database: {e}")
        raise e

def calculate_file_hash(content):
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def save_document_with_versioning(db, document_data, file_path, content, uploaded_by=None):
    """Save document with versioning support"""
    try:
        file_hash = calculate_file_hash(content)
        
        # Check if document with same name exists
        existing_doc = db.query(Document).filter(
            Document.name == document_data['name'],
            Document.is_latest == True
        ).first()
        
        if existing_doc:
            # Document exists, create new version
            print(f"📄 Document '{document_data['name']}' exists, creating new version")
            
            # Update existing document to not be latest
            existing_doc.is_latest = False
            existing_doc.version = existing_doc.version + 1
            
            # Create new version record
            new_version = DocumentVersion(
                id=str(uuid.uuid4()),
                document_id=existing_doc.id,
                version=existing_doc.version,
                file_path=file_path,
                content=content,
                file_hash=file_hash,
                uploaded_by=uploaded_by,
                file_size=document_data.get('size', 0)
            )
            db.add(new_version)
            
            # Create new document record (latest version)
            new_doc = Document(
                id=str(uuid.uuid4()),
                name=document_data['name'],
                file_type=document_data['fileType'],
                file_path=file_path,
                content=content,
                meta=document_data,
                file_hash=file_hash,
                version=existing_doc.version + 1,
                is_latest=True,
                original_document_id=existing_doc.original_document_id or existing_doc.id,
                uploaded_by=uploaded_by,
                file_size=document_data.get('size', 0)
            )
            db.add(new_doc)
            
            print(f"✅ New version {new_doc.version} created for document '{document_data['name']}'")
            return new_doc
            
        else:
            # New document, create first version
            print(f"📄 Creating new document '{document_data['name']}'")
            
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                name=document_data['name'],
                file_type=document_data['fileType'],
                file_path=file_path,
                content=content,
                meta=document_data,
                file_hash=file_hash,
                version=1,
                is_latest=True,
                original_document_id=doc_id,
                uploaded_by=uploaded_by,
                file_size=document_data.get('size', 0)
            )
            db.add(document)
            
            # Create first version record
            first_version = DocumentVersion(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                version=1,
                file_path=file_path,
                content=content,
                file_hash=file_hash,
                uploaded_by=uploaded_by,
                file_size=document_data.get('size', 0)
            )
            db.add(first_version)
            
            print(f"✅ New document '{document_data['name']}' created with version 1")
            return document
        
        db.commit()
        
    except Exception as e:
        print(f"❌ Error saving document with versioning: {e}")
        db.rollback()
        raise e

def get_document_versions(db, document_name):
    """Get all versions of a document"""
    try:
        # Get the original document ID
        original_doc = db.query(Document).filter(
            Document.name == document_name,
            Document.original_document_id == Document.id
        ).first()
        
        if not original_doc:
            return []
        
        # Get all versions
        versions = db.query(Document).filter(
            Document.original_document_id == original_doc.original_document_id
        ).order_by(Document.version.desc()).all()
        
        return [
            {
                'id': doc.id,
                'name': doc.name,
                'version': doc.version,
                'upload_date': doc.upload_date.isoformat(),
                'uploaded_by': doc.uploaded_by,
                'file_size': doc.file_size,
                'is_latest': doc.is_latest,
                'file_hash': doc.file_hash
            }
            for doc in versions
        ]
    except Exception as e:
        print(f"❌ Error getting document versions: {e}")
        return []

def get_latest_document(db, document_name):
    """Get the latest version of a document"""
    try:
        document = db.query(Document).filter(
            Document.name == document_name,
            Document.is_latest == True
        ).first()
        
        if document:
            return {
                'id': document.id,
                'name': document.name,
                'file_type': document.file_type,
                'upload_date': document.upload_date.isoformat(),
                'file_path': document.file_path,
                'content': document.content,
                'meta': document.meta,
                'status': document.status,
                'version': document.version,
                'uploaded_by': document.uploaded_by,
                'file_size': document.file_size
            }
        return None
    except Exception as e:
        print(f"❌ Error getting latest document: {e}")
        return None

def save_analysis_with_approval(db, analysis_data, document_id=None):
    """Save analysis with approval tracking"""
    try:
        # Create analysis
        analysis = Analysis(
            id=analysis_data['id'],
            title=analysis_data['title'],
            original_text=analysis_data['originalText'],
            results=analysis_data['results'],
            document_id=document_id,
            user_email=analysis_data.get('user_email'),
            analysis_type=analysis_data.get('analysis_type', 'general'),
            quality_score=analysis_data.get('quality_score', 0)
        )
        db.add(analysis)
        
        # Create initial approval record
        approval = Approval(
            id=str(uuid.uuid4()),
            analysis_id=analysis_data['id'],
            status="pending",
            approver_email=analysis_data.get('approver_email'),
            results_summary=analysis_data.get('results_summary', {})
        )
        db.add(approval)
        
        db.commit()
        print(f"✅ Analysis saved with approval tracking: {analysis_data['id']}")
        return analysis
        
    except Exception as e:
        print(f"❌ Error saving analysis with approval: {e}")
        db.rollback()
        raise e

def update_approval_status(db, approval_id, status, approver_email, notes=None):
    """Update approval status"""
    try:
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if approval:
            approval.status = status
            approval.approver_email = approver_email
            approval.updated_date = datetime.utcnow()
            approval.approval_notes = notes
            
            if status in ['approved', 'rejected']:
                approval.approval_date = datetime.utcnow()
            
            db.commit()
            print(f"✅ Approval status updated to '{status}' for {approval_id}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error updating approval status: {e}")
        db.rollback()
        return False

def get_pending_approvals(db, approver_email=None):
    """Get pending approvals"""
    try:
        query = db.query(Approval).filter(Approval.status == "pending")
        if approver_email:
            query = query.filter(Approval.approver_email == approver_email)
        
        approvals = query.all()
        return [
            {
                'id': approval.id,
                'analysis_id': approval.analysis_id,
                'status': approval.status,
                'created_date': approval.created_date.isoformat(),
                'approver_email': approval.approver_email,
                'results_summary': approval.results_summary
            }
            for approval in approvals
        ]
    except Exception as e:
        print(f"❌ Error getting pending approvals: {e}")
        return []

def get_all_documents_with_versions(db):
    """Get all documents with version information"""
    try:
        # Get latest versions of all documents
        documents = db.query(Document).filter(
            Document.is_latest == True
        ).order_by(Document.upload_date.desc()).all()
        
        result = []
        for doc in documents:
            # Get version count
            version_count = db.query(Document).filter(
                Document.original_document_id == doc.original_document_id
            ).count()
            
            result.append({
                'id': doc.id,
                'name': doc.name,
                'file_type': doc.file_type,
                'upload_date': doc.upload_date.isoformat(),
                'file_path': doc.file_path,
                'content': doc.content,
                'meta': doc.meta,
                'status': doc.status,
                'version': doc.version,
                'version_count': version_count,
                'uploaded_by': doc.uploaded_by,
                'file_size': doc.file_size,
                'is_latest': doc.is_latest
            })
        
        return result
    except Exception as e:
        print(f"❌ Error getting all documents with versions: {e}")
        return []

def check_document_exists_by_hash(db, content):
    """Check if document with same content already exists"""
    try:
        file_hash = calculate_file_hash(content)
        existing_doc = db.query(Document).filter(
            Document.file_hash == file_hash
        ).first()
        return existing_doc is not None
    except Exception as e:
        print(f"❌ Error checking document existence by hash: {e}")
        return False

def get_document_analyses(db, document_id):
    """Get all analyses for a document"""
    try:
        analyses = db.query(Analysis).filter(
            Analysis.document_id == document_id
        ).order_by(Analysis.date.desc()).all()
        
        return [
            {
                'id': analysis.id,
                'title': analysis.title,
                'date': analysis.date.isoformat(),
                'status': analysis.status,
                'analysis_type': analysis.analysis_type,
                'quality_score': analysis.quality_score,
                'user_email': analysis.user_email
            }
            for analysis in analyses
        ]
    except Exception as e:
        print(f"❌ Error getting document analyses: {e}")
        return []

# Test function
def test_enhanced_database():
    """Test the enhanced database functionality"""
    print("🧪 Testing Enhanced Database Functionality...")
    
    # Initialize database
    init_db()
    
    # Test document versioning
    db = next(get_db())
    try:
        # Test document creation
        test_doc_data = {
            'id': str(uuid.uuid4()),
            'name': 'test_document.pdf',
            'fileType': 'pdf',
            'size': 1024
        }
        
        test_content = "This is test content for versioning"
        test_path = "uploads/test_document.pdf"
        
        # Save first version
        doc1 = save_document_with_versioning(db, test_doc_data, test_path, test_content, "user1@test.com")
        print(f"✅ First version created: {doc1.version}")
        
        # Save second version (same name, different content)
        test_content2 = "This is updated test content for versioning"
        doc2 = save_document_with_versioning(db, test_doc_data, test_path, test_content2, "user2@test.com")
        print(f"✅ Second version created: {doc2.version}")
        
        # Get versions
        versions = get_document_versions(db, 'test_document.pdf')
        print(f"✅ Found {len(versions)} versions")
        
        # Get latest
        latest = get_latest_document(db, 'test_document.pdf')
        print(f"✅ Latest version: {latest['version']}")
        
        # Test analysis with approval
        analysis_data = {
            'id': str(uuid.uuid4()),
            'title': 'Test Analysis',
            'originalText': test_content2,
            'results': {'score': 85, 'type': 'HLD'},
            'user_email': 'user1@test.com',
            'analysis_type': 'HLD',
            'quality_score': 85
        }
        
        analysis = save_analysis_with_approval(db, analysis_data, doc2.id)
        print(f"✅ Analysis with approval created: {analysis.id}")
        
        # Test approval update
        approval_id = db.query(Approval).filter(Approval.analysis_id == analysis.id).first().id
        success = update_approval_status(db, approval_id, 'approved', 'approver@test.com', 'Good analysis')
        print(f"✅ Approval status updated: {success}")
        
        return {
            'success': True,
            'document_versions': len(versions),
            'latest_version': latest['version'],
            'analysis_created': analysis.id is not None,
            'approval_updated': success
        }
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    test_enhanced_database()
