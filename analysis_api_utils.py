from flask import jsonify
from database_enhanced import get_db
from database_enhanced import Analysis

def get_analysis_by_id(analysis_id):
    db = next(get_db())
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            # Convert analysis object to dict with all details
            return {
                'id': analysis.id,
                'title': analysis.title,
                'date': analysis.date.isoformat() if analysis.date else None,
                'status': analysis.status,
                'original_text': analysis.original_text,
                'results': analysis.results,
                'document_id': analysis.document_id,
                'user_email': analysis.user_email,
                'analysis_type': analysis.analysis_type,
                'quality_score': analysis.quality_score
            }
        else:
            return None
    finally:
        db.close()
