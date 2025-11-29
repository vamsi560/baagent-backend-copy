#!/usr/bin/env python3
"""
Minimal server test
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'message': 'Minimal server is running'
    }), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Minimal BA Agent Server is running!'
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Minimal Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
