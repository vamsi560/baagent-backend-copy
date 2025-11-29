# main_enhanced.py
# Enhanced main API with multi-user authentication and project management

import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
from datetime import datetime, timezone
from sqlalchemy import text

# Import our modules
from database_multi_user import (
    get_db, User, Project, Document, Analysis, TextInput, 
    create_project, get_user_projects, add_user_to_project,
    save_text_input, ProjectStatus, ProjectUserRole, project_documents
)
from auth_system import (
    auth_manager, token_required, role_required, project_access_required,
    register_user, login_user, get_user_profile, update_user_profile,
    change_password, logout_user, get_all_users, update_user_status
)
from model_orchestrator import ModelOrchestrator
from integration_services import IntegrationManager

# Initialize Flask app
app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
orchestrator = ModelOrchestrator()
integration_manager = IntegrationManager()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Register a new user"""
    return register_user()

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Login user"""
    return login_user()

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def api_logout():
    """Logout user"""
    return logout_user()

@app.route('/api/auth/profile', methods=['GET'])
@token_required
def api_get_profile():
    """Get user profile"""
    return get_user_profile()

@app.route('/api/auth/profile', methods=['PUT'])
@token_required
def api_update_profile():
    """Update user profile"""
    return update_user_profile()

@app.route('/api/auth/change-password', methods=['POST'])
@token_required
def api_change_password():
    """Change user password"""
    return change_password()

# Admin endpoints
@app.route('/api/admin/users', methods=['GET'])
@token_required
@role_required(['admin'])
def api_get_all_users():
    """Get all users (admin only)"""
    return get_all_users()

@app.route('/api/admin/users/status', methods=['PUT'])
@token_required
@role_required(['admin'])
def api_update_user_status():
    """Update user status (admin only)"""
    return update_user_status()

# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/projects', methods=['POST'])
@token_required
def create_project_api():
    """Create a new project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'message': 'Project name is required'}), 400
        
        db = next(get_db())
        try:
            # Create project
            project = create_project(
                db=db,
                name=name,
                description=description,
                owner_id=request.current_user['id']
            )
            
            # Add owner to project members
            add_user_to_project(db, request.current_user['id'], project.id, ProjectUserRole.OWNER)
            
            return jsonify({
                'message': 'Project created successfully',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'owner_id': project.owner_id,
                    'status': project.status,
                    'created_at': project.created_at.isoformat()
                }
            }), 201
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to create project: {str(e)}'}), 500

@app.route('/api/projects', methods=['GET'])
@token_required
def get_projects_api():
    """Get all projects for current user"""
    try:
        db = next(get_db())
        try:
            projects = get_user_projects(db, request.current_user['id'])
            
            return jsonify({
                'projects': projects
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get projects: {str(e)}'}), 500

@app.route('/api/projects/<project_id>', methods=['GET'])
@token_required
@project_access_required
def get_project_api(project_id):
    """Get specific project details"""
    try:
        db = next(get_db())
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            # Get project statistics
            doc_count = db.query(Document).join(
                project_documents
            ).filter(
                project_documents.c.project_id == project_id
            ).count()
            
            analysis_count = db.query(Analysis).filter(
                Analysis.project_id == project_id
            ).count()
            
            return jsonify({
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'owner_id': project.owner_id,
                    'status': project.status,
                    'created_at': project.created_at.isoformat(),
                    'updated_at': project.updated_at.isoformat(),
                    'statistics': {
                        'documents': doc_count,
                        'analyses': analysis_count
                    }
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get project: {str(e)}'}), 500

@app.route('/api/projects/<project_id>', methods=['PUT'])
@token_required
@project_access_required
def update_project_api(project_id):
    """Update project details"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        db = next(get_db())
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            # Update fields
            if 'name' in data:
                project.name = data['name']
            
            if 'description' in data:
                project.description = data['description']
            
            if 'status' in data:
                project.status = data['status']
            
            project.updated_at = datetime.now(timezone.utc)
            db.commit()
            
            return jsonify({
                'message': 'Project updated successfully',
                'project': {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'status': project.status,
                    'updated_at': project.updated_at.isoformat()
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to update project: {str(e)}'}), 500

@app.route('/api/projects/<project_id>/members', methods=['POST'])
@token_required
@project_access_required
def add_project_member_api(project_id):
    """Add member to project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        user_email = data.get('user_email')
        role = data.get('role', ProjectUserRole.MEMBER)
        
        if not user_email:
            return jsonify({'message': 'User email is required'}), 400
        
        db = next(get_db())
        try:
            # Find user by email
            user = db.query(User).filter(User.email == user_email).first()
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            # Add user to project
            success = add_user_to_project(db, user.id, project_id, role)
            
            if success:
                return jsonify({
                    'message': 'User added to project successfully',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'role': role
                    }
                }), 200
            else:
                return jsonify({'message': 'User is already a member of this project'}), 409
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to add member: {str(e)}'}), 500

# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/projects/<project_id>/documents', methods=['POST'])
@token_required
@project_access_required
def upload_document_api(project_id):
    """Upload document to project"""
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'File type not allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        db = next(get_db())
        try:
            # Create document
            document = Document(
                id=None,  # Auto-increment
                name=filename,
                file_type=filename.rsplit('.', 1)[1].lower(),
                file_path=file_path,
                content=content,
                status='uploaded',
                uploaded_by=request.current_user['id'],
                source_type='local'
            )
            
            db.add(document)
            db.flush()  # Get the ID
            
            # Link to project
            db.execute(text("""
                INSERT INTO project_documents (project_id, document_id, added_at)
                VALUES (:project_id, :document_id, :added_at)
            """), {
                'project_id': project_id,
                'document_id': document.id,
                'added_at': datetime.now(timezone.utc)
            })
            
            db.commit()
            
            return jsonify({
                'message': 'Document uploaded successfully',
                'document': {
                    'id': document.id,
                    'name': document.name,
                    'file_type': document.file_type,
                    'upload_date': document.upload_date.isoformat(),
                    'status': document.status
                }
            }), 201
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to upload document: {str(e)}'}), 500

@app.route('/api/projects/<project_id>/documents', methods=['GET'])
@token_required
@project_access_required
def get_project_documents_api(project_id):
    """Get all documents in project"""
    try:
        db = next(get_db())
        try:
            documents = db.query(Document).join(
                project_documents
            ).filter(
                project_documents.c.project_id == project_id
            ).all()
            
            return jsonify({
                'documents': [
                    {
                        'id': doc.id,
                        'name': doc.name,
                        'file_type': doc.file_type,
                        'upload_date': doc.upload_date.isoformat(),
                        'status': doc.status,
                        'uploaded_by': doc.uploaded_by
                    }
                    for doc in documents
                ]
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get documents: {str(e)}'}), 500

# ============================================================================
# TEXT INPUT ENDPOINTS
# ============================================================================

@app.route('/api/projects/<project_id>/text-inputs', methods=['POST'])
@token_required
@project_access_required
def create_text_input_api(project_id):
    """Create text input for project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        title = data.get('title')
        content = data.get('content')
        template_id = data.get('template_id')
        
        if not title or not content:
            return jsonify({'message': 'Title and content are required'}), 400
        
        db = next(get_db())
        try:
            # Save text input
            text_input = save_text_input(
                db=db,
                title=title,
                content=content,
                user_id=request.current_user['id'],
                project_id=project_id,
                template_id=template_id
            )
            
            return jsonify({
                'message': 'Text input created successfully',
                'text_input': {
                    'id': text_input.id,
                    'title': text_input.title,
                    'content': text_input.content,
                    'created_at': text_input.created_at.isoformat(),
                    'version': text_input.version
                }
            }), 201
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to create text input: {str(e)}'}), 500

@app.route('/api/projects/<project_id>/text-inputs', methods=['GET'])
@token_required
@project_access_required
def get_text_inputs_api(project_id):
    """Get all text inputs for project"""
    try:
        db = next(get_db())
        try:
            text_inputs = db.query(TextInput).filter(
                TextInput.project_id == project_id,
                TextInput.is_latest == True
            ).all()
            
            return jsonify({
                'text_inputs': [
                    {
                        'id': ti.id,
                        'title': ti.title,
                        'content': ti.content,
                        'created_at': ti.created_at.isoformat(),
                        'updated_at': ti.updated_at.isoformat(),
                        'version': ti.version,
                        'user_id': ti.user_id
                    }
                    for ti in text_inputs
                ]
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get text inputs: {str(e)}'}), 500

# ============================================================================
# ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/projects/<project_id>/analyze', methods=['POST'])
@token_required
@project_access_required
def analyze_project_api(project_id):
    """Analyze project documents and text inputs with TRD section selection"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        analysis_type = data.get('type', 'general')
        document_ids = data.get('document_ids', [])
        text_input_ids = data.get('text_input_ids', [])
        selected_sections = data.get('selected_sections', None)  # TRD sections to generate
        
        db = next(get_db())
        try:
            # Collect content for analysis
            content_parts = []
            
            # Add documents
            if document_ids:
                documents = db.query(Document).filter(
                    Document.id.in_(document_ids)
                ).all()
                
                for doc in documents:
                    content_parts.append(f"Document: {doc.name}\n{doc.content}")
            
            # Add text inputs
            if text_input_ids:
                text_inputs = db.query(TextInput).filter(
                    TextInput.id.in_(text_input_ids)
                ).all()
                
                for ti in text_inputs:
                    content_parts.append(f"Text Input: {ti.title}\n{ti.content}")
            
            if not content_parts:
                return jsonify({'message': 'No content provided for analysis'}), 400
            
            # Combine content
            combined_content = "\n\n".join(content_parts)
            
            # Perform analysis with section selection for TRD
            if analysis_type == 'trd' and selected_sections:
                # Use document generation engine with section selection
                from document_generation_engine import DocumentGenerationEngine
                doc_engine = DocumentGenerationEngine()
                
                # Generate TRD with selected sections
                result = orchestrator.process_document_analysis(combined_content)
                
                # If TRD generation, use custom function with sections
                if result['success']:
                    # For now, use the standard analysis
                    # TODO: Integrate section selection into document generation
                    pass
            else:
                # Perform standard analysis
                result = orchestrator.analyze_document(combined_content)
            
            if result['success']:
                # Save analysis
                analysis = Analysis(
                    id=str(uuid.uuid4()),
                    title=f"Project Analysis - {analysis_type}",
                    original_text=combined_content,
                    results=result['response'],
                    user_id=request.current_user['id'],
                    analysis_type=analysis_type,
                    project_id=project_id,
                    quality_score=result.get('accuracy', 80)
                )
                
                db.add(analysis)
                db.commit()
                
                return jsonify({
                    'message': 'Analysis completed successfully',
                    'analysis': {
                        'id': analysis.id,
                        'title': analysis.title,
                        'results': analysis.results,
                        'quality_score': analysis.quality_score,
                        'created_at': analysis.date.isoformat()
                    }
                }), 200
            else:
                return jsonify({'message': 'Analysis failed', 'error': result['response']}), 500
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/projects/<project_id>/analyses', methods=['GET'])
@token_required
@project_access_required
def get_project_analyses_api(project_id):
    """Get all analyses for project"""
    try:
        db = next(get_db())
        try:
            analyses = db.query(Analysis).filter(
                Analysis.project_id == project_id
            ).order_by(Analysis.date.desc()).all()
            
            return jsonify({
                'analyses': [
                    {
                        'id': analysis.id,
                        'title': analysis.title,
                        'results': analysis.results,
                        'analysis_type': analysis.analysis_type,
                        'quality_score': analysis.quality_score,
                        'created_at': analysis.date.isoformat(),
                        'user_id': analysis.user_id
                    }
                    for analysis in analyses
                ]
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get analyses: {str(e)}'}), 500

# ============================================================================
# INTEGRATION ENDPOINTS
# ============================================================================

@app.route('/api/integrations/ado/connect', methods=['POST'])
@token_required
def connect_azure_devops_api():
    """Connect to Azure DevOps"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        org_url = data.get('organization_url')
        pat_token = data.get('pat_token')
        
        if not org_url or not pat_token:
            return jsonify({'message': 'Organization URL and PAT token are required'}), 400
        
        # Setup connection
        success = integration_manager.setup_azure_devops(org_url, pat_token)
        
        if success:
            return jsonify({
                'message': 'Azure DevOps connected successfully'
            }), 200
        else:
            return jsonify({'message': 'Failed to connect to Azure DevOps'}), 500
        
    except Exception as e:
        return jsonify({'message': f'Failed to connect to Azure DevOps: {str(e)}'}), 500

@app.route('/api/integrations/ado/projects', methods=['GET'])
@token_required
def get_ado_projects_api():
    """Get Azure DevOps projects"""
    try:
        org_url = request.args.get('organization_url')
        
        if not org_url:
            return jsonify({'message': 'Organization URL is required'}), 400
        
        projects = integration_manager.get_ado_projects(org_url)
        
        return jsonify({
            'projects': projects
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get Azure DevOps projects: {str(e)}'}), 500

# ============================================================================
# HEALTH CHECK AND SYSTEM STATUS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        # Check orchestrator status
        status = orchestrator.get_system_status()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'orchestrator': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/system/status', methods=['GET'])
@token_required
def system_status():
    """Get system status"""
    try:
        status = orchestrator.get_system_status()
        
        return jsonify({
            'system_status': status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get system status: {str(e)}'}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'message': 'File too large'}), 413

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Enhanced BA Agent API...")
    print("✅ Multi-user authentication enabled")
    print("✅ Project management enabled")
    print("✅ Integration services enabled")
    print("✅ Document analysis enabled")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
