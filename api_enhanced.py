# api_enhanced.py
# Enhanced API endpoints for document versioning, storage, and approval management

from flask import Blueprint, request, jsonify
from analysis_api_utils import get_analysis_by_id
from database_enhanced import (
    get_db, save_document_with_versioning, get_document_versions, 
    get_latest_document, save_analysis_with_approval, update_approval_status,
    get_pending_approvals, get_all_documents_with_versions, 
    get_document_analyses, check_document_exists_by_hash
)
from model_orchestrator import ModelOrchestrator
import uuid
from datetime import datetime
import os

# Create Blueprint for enhanced API
api_enhanced = Blueprint('api_enhanced', __name__)

# Initialize Model Orchestrator
orchestrator = ModelOrchestrator()

@api_enhanced.route("/api/enhanced/upload_document", methods=['POST'])
def enhanced_upload_document():
    """Enhanced document upload with versioning"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        uploaded_by = request.form.get('uploaded_by', 'unknown@user.com')
        
        print(f"📥 [Enhanced Upload] Started for file: {file.filename}")

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith(('.pdf', '.docx')):
            return jsonify({"error": "Only PDF and DOCX files are allowed"}), 400

        # Read file content
        file_content_bytes = file.read()
        file_size = len(file_content_bytes)
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Extract content from file (you'll need to implement this)
        # For now, we'll use a placeholder
        file_content = file_content_bytes.decode('utf-8', errors='ignore')
        
        # Check if document with same content already exists
        db = next(get_db())
        try:
            if check_document_exists_by_hash(db, file_content):
                return jsonify({
                    "error": "Document with identical content already exists",
                    "duplicate": True
                }), 409
            
            # Create document data
            doc_id = str(uuid.uuid4())
            file_path = f"{uploads_dir}/{doc_id}_{file.filename}"
            
            # Save file to disk
            with open(file_path, 'wb') as f:
                f.write(file_content_bytes)
            
            document_data = {
                'id': doc_id,
                'name': file.filename,
                'fileType': file.filename.split('.')[-1].lower(),
                'size': file_size
            }
            
            # Save document with versioning
            document = save_document_with_versioning(db, document_data, file_path, file_content, uploaded_by)
            
            return jsonify({
                "success": True,
                "message": "Document uploaded successfully with versioning",
                "document": {
                    "id": document.id,
                    "name": document.name,
                    "version": document.version,
                    "upload_date": document.upload_date.isoformat(),
                    "uploaded_by": document.uploaded_by,
                    "file_size": document.file_size,
                    "is_latest": document.is_latest
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error in enhanced upload: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/documents", methods=['GET'])
def get_enhanced_documents():
    """Get all documents with version information"""
    try:
        db = next(get_db())
        try:
            documents = get_all_documents_with_versions(db)
            return jsonify({
                "success": True,
                "documents": documents
            }), 200
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error getting enhanced documents: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/documents/<document_name>/versions", methods=['GET'])
def get_document_versions_api(document_name):
    """Get all versions of a specific document"""
    try:
        db = next(get_db())
        try:
            versions = get_document_versions(db, document_name)
            return jsonify({
                "success": True,
                "document_name": document_name,
                "versions": versions
            }), 200
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error getting document versions: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/documents/<document_name>/latest", methods=['GET'])
def get_latest_document_api(document_name):
    """Get the latest version of a document"""
    try:
        db = next(get_db())
        try:
            document = get_latest_document(db, document_name)
            if document:
                return jsonify({
                    "success": True,
                    "document": document
                }), 200
            else:
                return jsonify({"error": "Document not found"}), 404
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error getting latest document: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/analyze_document", methods=['POST'])
def enhanced_analyze_document():
    """Enhanced document analysis with approval tracking"""
    try:
        data = request.get_json()
        document_name = data.get('document_name')
        analysis_type = data.get('analysis_type', 'general')
        user_email = data.get('user_email', 'unknown@user.com')
        
        if not document_name:
            return jsonify({"error": "Document name is required"}), 400
        
        db = next(get_db())
        try:
            # Get latest document
            document = get_latest_document(db, document_name)
            if not document:
                return jsonify({"error": "Document not found"}), 404
            
            # Perform analysis using orchestrator
            if analysis_type == 'HLD':
                result = orchestrator.process_hld_generation(document['content'])
            elif analysis_type == 'LLD':
                # For LLD, we need HLD content first
                hld_result = orchestrator.process_hld_generation(document['content'])
                if hld_result['success']:
                    result = orchestrator.process_lld_generation(document['content'], hld_result['hld_content'])
                else:
                    return jsonify({"error": "HLD generation failed"}), 500
            elif analysis_type == 'Backlog':
                result = orchestrator.process_backlog_generation(document['content'])
            else:
                result = orchestrator.process_document_analysis(document['content'])
            
            if result['success']:
                # Save analysis with approval tracking
                analysis_data = {
                    'id': str(uuid.uuid4()),
                    'title': f"{analysis_type} Analysis - {document_name}",
                    'originalText': document['content'],
                    'results': result,
                    'user_email': user_email,
                    'analysis_type': analysis_type,
                    'quality_score': result.get('quality_score', 0),
                    'approver_email': data.get('approver_email')
                }
                
                analysis = save_analysis_with_approval(db, analysis_data, document['id'])
                
                return jsonify({
                    "success": True,
                    "analysis": {
                        "id": analysis.id,
                        "title": analysis.title,
                        "analysis_type": analysis.analysis_type,
                        "quality_score": analysis.quality_score,
                        "status": "pending_approval"
                    },
                    "result": result
                }), 200
            else:
                return jsonify({"error": "Analysis failed"}), 500
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error in enhanced analysis: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/approvals", methods=['GET'])
def get_approvals():
    """Get pending approvals"""
    try:
        approver_email = request.args.get('approver_email')
        db = next(get_db())
        try:
            approvals = get_pending_approvals(db, approver_email)
            return jsonify({
                "success": True,
                "approvals": approvals
            }), 200
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error getting approvals: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/approvals/<approval_id>", methods=['PUT'])
def update_approval():
    """Update approval status"""
    try:
        data = request.get_json()
        status = data.get('status')
        approver_email = data.get('approver_email')
        notes = data.get('notes')
        
        if not status or not approver_email:
            return jsonify({"error": "Status and approver_email are required"}), 400
        
        db = next(get_db())
        try:
            success = update_approval_status(db, approval_id, status, approver_email, notes)
            if success:
                return jsonify({
                    "success": True,
                    "message": f"Approval status updated to {status}"
                }), 200
            else:
                return jsonify({"error": "Approval not found"}), 404
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error updating approval: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/documents/<document_name>/analyses", methods=['GET'])
def get_document_analyses_api(document_name):
    """Get all analyses for a document"""
    try:
        db = next(get_db())
        try:
            # Get latest document
            document = get_latest_document(db, document_name)
            if not document:
                return jsonify({"error": "Document not found"}), 404
            
            analyses = get_document_analyses(db, document['id'])
            return jsonify({
                "success": True,
                "document_name": document_name,
                "analyses": analyses
            }), 200
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error getting document analyses: {e}")
        return jsonify({"error": str(e)}), 500

@api_enhanced.route("/api/enhanced/documents/<document_name>/upload_new_version", methods=['POST'])
def upload_new_version():
    """Upload a new version of an existing document"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        uploaded_by = request.form.get('uploaded_by', 'unknown@user.com')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith(('.pdf', '.docx')):
            return jsonify({"error": "Only PDF and DOCX files are allowed"}), 400

        # Read file content
        file_content_bytes = file.read()
        file_size = len(file_content_bytes)
        file_content = file_content_bytes.decode('utf-8', errors='ignore')
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Check if document exists
        db = next(get_db())
        try:
            existing_doc = get_latest_document(db, document_name)
            if not existing_doc:
                return jsonify({"error": "Original document not found"}), 404
            
            # Create new version
            doc_id = str(uuid.uuid4())
            file_path = f"{uploads_dir}/{doc_id}_{file.filename}"
            
            # Save file to disk
            with open(file_path, 'wb') as f:
                f.write(file_content_bytes)
            
            document_data = {
                'id': doc_id,
                'name': document_name,  # Keep same name for versioning
                'fileType': file.filename.split('.')[-1].lower(),
                'size': file_size
            }
            
            # Save new version
            document = save_document_with_versioning(db, document_data, file_path, file_content, uploaded_by)
            
            return jsonify({
                "success": True,
                "message": f"New version {document.version} uploaded successfully",
                "document": {
                    "id": document.id,
                    "name": document.name,
                    "version": document.version,
                    "upload_date": document.upload_date.isoformat(),
                    "uploaded_by": document.uploaded_by,
                    "file_size": document.file_size,
                    "is_latest": document.is_latest
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error uploading new version: {e}")
        return jsonify({"error": str(e)}), 500

# Test endpoint
@api_enhanced.route("/api/enhanced/test", methods=['GET'])
def test_enhanced_api():
    """Test the enhanced API functionality"""
    try:
        from database_enhanced import test_enhanced_database
        result = test_enhanced_database()
        return jsonify({
            "success": True,
            "test_result": result
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# New endpoint: GET /api/enhanced/analyses/<analysis_id>
@api_enhanced.route("/api/enhanced/analyses/<analysis_id>", methods=['GET'])
def get_analysis_details_by_id(analysis_id):
    """Retrieve full analysis details by ID"""
    try:
        analysis = get_analysis_by_id(analysis_id)
        if analysis:
            return jsonify({
                "success": True,
                "analysis": analysis
            }), 200
        else:
            return jsonify({
                "error": f"Analysis with ID {analysis_id} not found"
            }), 404
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
