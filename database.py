# database.py
# Fresh Database Configuration for BA Agent

import os
import uuid
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2.extras import RealDictCursor

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# PostgreSQL Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://bauser:Valuemomentum123@baagent.postgres.database.azure.com:5432/ba_agent')

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pinecone Vector Database Configuration
PINECONE_ENABLED = os.getenv('PINECONE_ENABLED', 'true').lower() == 'true'
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'pcsk_4B1bSV_9t2GM5KafTYtQ6iDEkKjS1cEX2kr9Zbyp5Dg2oA9Mp8hwgQnPo1SdwVbiUZ1s1i')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'ba-agent-documents')
VECTOR_SIZE = 384  # Dimension for all-MiniLM-L6-v2 embeddings

# Initialize Pinecone client and embedding model
pinecone_client = None
embedding_model = None

if PINECONE_ENABLED:
    # Initialize Pinecone (separate from embedding model)
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_client = pc
        print("SUCCESS: Pinecone initialized successfully")
    except ImportError as e:
        print(f"WARNING: Pinecone package not installed: {e}")
        print("   Install with: pip install pinecone")
        pinecone_client = None
    except Exception as e:
        print(f"WARNING: Pinecone initialization failed: {e}")
        pinecone_client = None
    
    # Initialize embedding model (separate from Pinecone)
    # Force CPU-only to avoid CUDA dependencies
    try:
        import os
        # Ensure PyTorch uses CPU only
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model (CPU-only, this may take a moment)...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        print("SUCCESS: Embedding model initialized successfully (CPU-only)")
    except ImportError as e:
        print(f"WARNING: sentence-transformers not installed: {e}")
        print("   Install with: pip install sentence-transformers")
        print("   For CPU-only: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
        embedding_model = None
    except Exception as e:
        print(f"WARNING: Embedding model initialization failed: {e}")
        print("   This may be due to torch/torchvision compatibility issues")
        print("   For CPU-only: pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu")
        embedding_model = None
else:
    print("INFO: Pinecone disabled")

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Document(Base):
    """Document model for storing uploaded files"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    user_email = Column(String, nullable=False, default="guest")
    name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    content = Column(Text)
    meta = Column(JSON)
    status = Column(String, default="uploaded")

class Analysis(Base):
    """Analysis model for storing analysis results"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    original_text = Column(Text)
    results = Column(JSON)
    document_id = Column(String)
    user_email = Column(String)

class Approval(Base):
    """Approval model for tracking approval workflow"""
    __tablename__ = "approvals"
    
    id = Column(String, primary_key=True)
    analysis_id = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow)
    approver_email = Column(String)
    results_summary = Column(JSON)
    approver_response = Column(String)
    ado_result = Column(JSON)

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables and Pinecone index"""
    try:
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: Database tables created successfully")
        
        # Initialize Pinecone index if enabled
        if PINECONE_ENABLED:
            init_pinecone_index()
            
    except Exception as e:
        print(f"ERROR: Error initializing database: {e}")
        raise e

def init_pinecone_index():
    """Initialize Pinecone index for document embeddings"""
    try:
        if not pinecone_client:
            print("WARNING: Pinecone client not initialized")
            return
        
        # Check if index exists (new Pinecone API)
        existing_indexes = pinecone_client.list_indexes()
        index_names = [idx.name for idx in existing_indexes] if existing_indexes else []
        
        if PINECONE_INDEX_NAME not in index_names:
            # Create index (new Pinecone API requires spec parameter)
            print(f"Creating Pinecone index: {PINECONE_INDEX_NAME}")
            try:
                from pinecone import ServerlessSpec
                pinecone_client.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=VECTOR_SIZE,
                    metric='cosine',
                    spec=ServerlessSpec(cloud='aws', region='us-east-1')
                )
                print(f"SUCCESS: Pinecone index '{PINECONE_INDEX_NAME}' created successfully")
            except Exception as e:
                print(f"WARNING: Could not create index (may already exist): {e}")
                # Try without spec (for older API or if already exists)
                try:
                    pinecone_client.create_index(
                        name=PINECONE_INDEX_NAME,
                        dimension=VECTOR_SIZE,
                        metric='cosine'
                    )
                except:
                    pass
        else:
            print(f"SUCCESS: Pinecone index '{PINECONE_INDEX_NAME}' already exists")
            
    except Exception as e:
        print(f"WARNING: Error initializing Pinecone index: {e}")

# ============================================================================
# DOCUMENT OPERATIONS
# ============================================================================

def save_document_to_db(db, user_email: str, file_name: str, file_type: str, file_path: str, file_content: str, meta: dict, status: str):
    """Save document to database"""
    try:
        # Use the ID from meta if available, otherwise generate new one
        doc_id = meta.get('id', str(uuid.uuid4()))
        
        new_doc = Document(
            id=doc_id,
            user_email=user_email,
            name=file_name,
            file_type=file_type,
            upload_date=datetime.utcnow(),
            file_path=file_path,
            content=file_content,
            meta=meta,
            status=status
        )
        db.add(new_doc)
        db.commit()
        print(f"✅ Document saved to database: {new_doc.id}")
        return new_doc
    except Exception as e:
        print(f"❌ Failed to save document: {e}")
        db.rollback()
        return None

def get_all_documents_from_db(db):
    """Get all documents from database"""
    try:
        documents = db.query(Document).order_by(Document.upload_date.desc()).all()
        return [
            {
                'id': doc.id,
                'name': doc.name,
                'file_type': doc.file_type,
                'upload_date': doc.upload_date.isoformat(),
                'file_path': doc.file_path,
                'content': doc.content,
                'meta': doc.meta,
                'status': doc.status,
                'user_email': doc.user_email
            }
            for doc in documents
        ]
    except Exception as e:
        print(f"❌ Error getting documents: {e}")
        return []

def get_document_by_id(db, doc_id: str):
    """Get document by ID"""
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            return {
                'id': doc.id,
                'name': doc.name,
                'file_type': doc.file_type,
                'upload_date': doc.upload_date.isoformat(),
                'file_path': doc.file_path,
                'content': doc.content,
                'meta': doc.meta,
                'status': doc.status,
                'user_email': doc.user_email
            }
        return None
    except Exception as e:
        print(f"❌ Error getting document: {e}")
        return None

def check_document_exists_by_name(db, filename: str):
    """Check if document exists by name"""
    try:
        doc = db.query(Document).filter(Document.name == filename).first()
        return doc is not None
    except Exception as e:
        print(f"❌ Error checking document existence: {e}")
        return False

# ============================================================================
# ANALYSIS OPERATIONS
# ============================================================================

def save_analysis_to_db(db, analysis_data: dict):
    """Save analysis to database"""
    try:
        analysis = Analysis(
            id=analysis_data['id'],
            title=analysis_data['title'],
            original_text=analysis_data['originalText'],
            results=analysis_data['results'],
            document_id=analysis_data.get('document_id'),
            user_email=analysis_data.get('user_email')
        )
        db.add(analysis)
        db.commit()
        print(f"✅ Analysis saved to database: {analysis.id}")
        return analysis
    except Exception as e:
        print(f"❌ Failed to save analysis: {e}")
        db.rollback()
        return None

def get_all_analyses_from_db(db, limit=50, offset=0):
    """Get analyses from database with pagination to avoid memory issues"""
    try:
        # Only select essential fields to avoid memory issues
        analyses = db.query(
            Analysis.id,
            Analysis.title,
            Analysis.date,
            Analysis.status,
            Analysis.document_id,
            Analysis.user_email
        ).order_by(Analysis.date.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                'id': analysis.id,
                'title': analysis.title,
                'date': analysis.date.isoformat(),
                'status': analysis.status,
                'document_id': analysis.document_id,
                'user_email': analysis.user_email,
                'original_text': None,  # Not loaded to save memory
                'results': None  # Not loaded to save memory
            }
            for analysis in analyses
        ]
    except Exception as e:
        print(f"❌ Error getting analyses: {e}")
        return []

def get_analysis_details_from_db(db, analysis_id):
    """Get full analysis details including original_text and results for a specific analysis"""
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            return {
                'id': analysis.id,
                'title': analysis.title,
                'date': analysis.date.isoformat(),
                'status': analysis.status,
                'original_text': analysis.original_text,
                'results': analysis.results,
                'document_id': analysis.document_id,
                'user_email': analysis.user_email
            }
        return None
    except Exception as e:
        print(f"❌ Error getting analysis details: {e}")
        return None

def get_analysis_by_id_from_db(db, analysis_id: str):
    """Get analysis by ID"""
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            return {
                'id': analysis.id,
                'title': analysis.title,
                'date': analysis.date.isoformat(),
                'status': analysis.status,
                'original_text': analysis.original_text,
                'results': analysis.results,
                'document_id': analysis.document_id,
                'user_email': analysis.user_email
            }
        return None
    except Exception as e:
        print(f"❌ Error getting analysis: {e}")
        return None

# ============================================================================
# APPROVAL OPERATIONS
# ============================================================================

def save_approval_to_db(db, approval_data: dict):
    """Save approval to database"""
    try:
        approval = Approval(
            id=approval_data['id'],
            analysis_id=approval_data['analysis_id'],
            status=approval_data['status'],
            created_date=datetime.fromisoformat(approval_data['created_date']),
            updated_date=datetime.fromisoformat(approval_data['updated_date']),
            approver_email=approval_data['approver_email'],
            results_summary=approval_data['results_summary']
        )
        db.add(approval)
        db.commit()
        print(f"✅ Approval saved to database: {approval.id}")
        return approval
    except Exception as e:
        print(f"❌ Failed to save approval: {e}")
        db.rollback()
        return None

def get_approval_from_db(db, approval_id: str):
    """Get approval from database"""
    try:
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if approval:
            return {
                'id': approval.id,
                'analysis_id': approval.analysis_id,
                'status': approval.status,
                'created_date': approval.created_date.isoformat(),
                'updated_date': approval.updated_date.isoformat(),
                'approver_email': approval.approver_email,
                'results_summary': approval.results_summary,
                'approver_response': approval.approver_response,
                'ado_result': approval.ado_result
            }
        return None
    except Exception as e:
        print(f"❌ Error getting approval: {e}")
        return None

def update_approval_in_db(db, approval_id: str, new_status: str):
    """Update approval status"""
    try:
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if approval:
            approval.status = new_status
            approval.updated_date = datetime.utcnow()
            db.commit()
            print(f"✅ Approval status updated: {approval_id} -> {new_status}")
            return approval
        return None
    except Exception as e:
        print(f"❌ Failed to update approval: {e}")
        db.rollback()
        return None

def update_approval_in_db_with_data(db, approval_id: str, update_data: dict):
    """Update approval with additional data"""
    try:
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if approval:
            if 'status' in update_data:
                approval.status = update_data['status']
            if 'updated_date' in update_data:
                approval.updated_date = datetime.fromisoformat(update_data['updated_date'])
            if 'approver_response' in update_data:
                approval.approver_response = update_data['approver_response']
            if 'ado_result' in update_data:
                approval.ado_result = update_data['ado_result']
            
            db.commit()
            print(f"✅ Approval updated with data: {approval_id}")
            return approval
        return None
    except Exception as e:
        print(f"❌ Failed to update approval with data: {e}")
        db.rollback()
        return None

# ============================================================================
# VECTOR DATABASE OPERATIONS (Pinecone)
# ============================================================================

def add_to_vector_db(content: str, meta: dict, lob: str = None):
    """Add content to Pinecone vector database"""
    if not PINECONE_ENABLED or not embedding_model or not pinecone_client:
        print("Vector database not available")
        return
    
    try:
        # Generate embedding
        embedding = embedding_model.encode(content).tolist()
        
        # Create ID
        doc_id = meta.get('id', str(uuid.uuid4()))
        
        # Prepare metadata for Pinecone
        pinecone_meta = {
            'document_id': meta.get('document_id', ''),
            'document_name': meta.get('document_name', meta.get('name', '')),
            'content': content[:5000],  # Limit content size for metadata
            'lob': lob or meta.get('lob', 'personal_auto'),
            'source': meta.get('source', 'upload'),
            **{k: v for k, v in meta.items() if k not in ['id', 'document_id', 'name', 'lob', 'source']}
        }
        
        # Get index (new Pinecone API)
        index = pinecone_client.Index(PINECONE_INDEX_NAME)
        
        # Upsert to Pinecone
        index.upsert(vectors=[{
            'id': doc_id,
            'values': embedding,
            'metadata': pinecone_meta
        }])
        
        print(f"SUCCESS: Added to Pinecone: {doc_id}")
    except Exception as e:
        print(f"ERROR: Failed to add to Pinecone: {e}")

def search_vector_db(query: str, lob: str = None, limit: int = 10):
    """Search Pinecone vector database using cosine similarity"""
    if not PINECONE_ENABLED or not embedding_model or not pinecone_client:
        print("Vector database not available")
        return []
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode(query).tolist()
        
        # Get index (new Pinecone API)
        index = pinecone_client.Index(PINECONE_INDEX_NAME)
        
        # Build filter for LOB if provided
        filter_dict = None
        if lob:
            filter_dict = {'lob': {'$eq': lob}}
        
        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        formatted_results = []
        for match in results.get('matches', []):
            formatted_results.append({
                'id': match['id'],
                'document_id': match['metadata'].get('document_id', ''),
                'content': match['metadata'].get('content', ''),
                'score': float(match['score']),
                'metadata': match['metadata'],
                'lob': match['metadata'].get('lob', 'personal_auto')
            })
        
        return formatted_results
    except Exception as e:
        print(f"ERROR: Failed to search Pinecone: {e}")
        return []

def delete_from_vector_db(doc_id: str):
    """Delete from Pinecone vector database"""
    if not PINECONE_ENABLED or not pinecone_client:
        print("Vector database not available")
        return
    
    try:
        # Get index (new Pinecone API)
        index = pinecone_client.Index(PINECONE_INDEX_NAME)
        
        # Delete from Pinecone
        index.delete(ids=[doc_id])
        
        print(f"SUCCESS: Deleted from Pinecone: {doc_id}")
    except Exception as e:
        print(f"ERROR: Failed to delete from Pinecone: {e}")

# ============================================================================
# DIRECT DATABASE OPERATIONS (for compatibility)
# ============================================================================

def save_document_to_db_direct(filename: str, file_type: str, file_path: str, content: str):
    """Save document using direct psycopg2 connection"""
    try:
        # Extract connection details from DATABASE_URL
        db_url = DATABASE_URL.replace('postgresql+psycopg2://', '')
        user_pass, host_port_db = db_url.split('@')
        user, password = user_pass.split(':')
        host_port, dbname = host_port_db.split('/')
        host, port = host_port.split(':')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO documents (id, user_email, name, file_type, file_path, content, upload_date, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (str(uuid.uuid4()), "guest", filename, file_type, file_path, content, datetime.utcnow(), "uploaded")
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Document saved directly: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save document directly: {e}")
        return False

def get_all_documents_from_db_direct():
    """Get all documents using direct psycopg2 connection"""
    try:
        # Extract connection details from DATABASE_URL
        db_url = DATABASE_URL.replace('postgresql+psycopg2://', '')
        user_pass, host_port_db = db_url.split('@')
        user, password = user_pass.split(':')
        host_port, dbname = host_port_db.split('/')
        host, port = host_port.split(':')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM documents ORDER BY upload_date DESC")
        documents = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [dict(doc) for doc in documents]
    except Exception as e:
        print(f"❌ Failed to get documents directly: {e}")
        return []

def check_document_exists_by_name_direct(filename: str):
    """Check if document exists by name using direct connection"""
    try:
        # Extract connection details from DATABASE_URL
        db_url = DATABASE_URL.replace('postgresql+psycopg2://', '')
        user_pass, host_port_db = db_url.split('@')
        user, password = user_pass.split(':')
        host_port, dbname = host_port_db.split('/')
        host, port = host_port.split(':')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE name = %s", (filename,))
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count > 0
    except Exception as e:
        print(f"❌ Failed to check document existence directly: {e}")
        return False
