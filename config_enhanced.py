# config_enhanced.py
# Enhanced Configuration for Advanced Features

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CORE CONFIGURATION
# ============================================================================


# Database Configuration
DATABASE_URL = 'postgresql+psycopg2://bauser:Valuemomentum123@baagent.postgres.database.azure.com:5432/ba_agent'

# Pinecone Vector Database Configuration
PINECONE_ENABLED = True
PINECONE_API_KEY = 'pcsk_4B1bSV_9t2GM5KafTYtQ6iDEkKjS1cEX2kr9Zbyp5Dg2oA9Mp8hwgQnPo1SdwVbiUZ1s1i'
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'ba-agent-documents')

# ============================================================================
# AI/ML CONFIGURATION
# ============================================================================

# Gemini API Configuration
GEMINI_API_KEY = 'AIzaSyA5_KnR58T2MTG4oOvBeAqbd8idJCdOlRA'
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# OpenAI Configuration (for LangChain)
OPENAI_API_KEY = ''
OPENAI_MODEL = 'gpt-4'

# LangChain Configuration
LANGCHAIN_TRACING_V2 = False
LANGCHAIN_ENDPOINT = ''
LANGCHAIN_API_KEY = ''
LANGCHAIN_PROJECT = 'ba-agent'

# Embedding Model Configuration
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
EMBEDDING_DEVICE = 'cpu'

# ============================================================================
# AZURE INTEGRATION
# ============================================================================

# Azure Communication Services
ACS_CONNECTION_STRING = 'endpoint=https://baagentacs123.india.communication.azure.com/;accesskey=3NFm6rs3wKyuP2B5BljzjkjGlWUC7SXWIilVOiHlF0jlpJQ8PiQ6JQQJ99BIACULyCpAhliiAAAAAZCSEmoo'
ACS_SENDER_ADDRESS = 'DoNotReply@0a996688-51d4-48e5-a65c-ad35a83a9c77.azurecomm.net'

# Azure DevOps Configuration
ADO_ORGANIZATION_URL = 'https://dev.azure.com/prayankagochipatula/'
ADO_PROJECT_NAME = 'Backstage'
ADO_PAT = 'DHDzeRhCouK9QI5q2q0cgu7OJpwKU7bJzkwvq2HxZhOquS4qkdxUJQQJ99BIACAAAAAAhliiAAASAZDO39lF'

# OneDrive Configuration - REMOVED

# ============================================================================
# EMAIL AND NOTIFICATIONS
# ============================================================================

APPROVAL_RECIPIENT_EMAIL = os.getenv('APPROVAL_RECIPIENT_EMAIL', 'Raghavendra.Lakkamaraju@valuemomentum.com')
BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://127.0.0.1:5000')

# ============================================================================
# LANGCHAIN ADVANCED FEATURES
# ============================================================================

# Memory Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
MEMORY_TYPE = os.getenv('MEMORY_TYPE', 'conversation_buffer')  # conversation_buffer, conversation_summary, redis

# Vector Store Configuration
VECTOR_STORE_TYPE = os.getenv('VECTOR_STORE_TYPE', 'qdrant')  # qdrant, pinecone, weaviate, faiss
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', '')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', '')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'ba-agent')

# Document Processing Configuration
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 8192))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))

# ============================================================================
# ANALYTICS AND MONITORING
# ============================================================================

# Prometheus Configuration
PROMETHEUS_ENABLED = os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true'
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9090))

# Sentry Configuration
SENTRY_DSN = os.getenv('SENTRY_DSN', '')
SENTRY_ENVIRONMENT = os.getenv('SENTRY_ENVIRONMENT', 'development')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')

# ============================================================================
# PERFORMANCE AND SCALING
# ============================================================================

# Async Configuration
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 10))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 120))

# Caching Configuration
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour

# Celery Configuration (for background tasks)
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# CORS Configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_HEADERS = ['Content-Type', 'Authorization']

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))  # requests per minute
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # seconds

# ============================================================================
# FILE PROCESSING CONFIGURATION
# ============================================================================

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,txt,md').split(',')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

# Image Processing Configuration
IMAGE_PROCESSING_ENABLED = os.getenv('IMAGE_PROCESSING_ENABLED', 'true').lower() == 'true'
MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10 * 1024 * 1024))  # 10MB
SUPPORTED_IMAGE_FORMATS = os.getenv('SUPPORTED_IMAGE_FORMATS', 'jpeg,png,webp,heic').split(',')

# ============================================================================
# TEMPLATE CONFIGURATION
# ============================================================================

# Template System Configuration
TEMPLATES_ENABLED = os.getenv('TEMPLATES_ENABLED', 'true').lower() == 'true'
TEMPLATES_DIR = os.getenv('TEMPLATES_DIR', 'templates')
CUSTOM_TEMPLATES_ENABLED = os.getenv('CUSTOM_TEMPLATES_ENABLED', 'true').lower() == 'true'

# Industry-Specific Templates
INDUSTRY_TEMPLATES = {
    'finance': {
        'compliance': ['SOX', 'PCI-DSS', 'GDPR'],
        'security_level': 'high',
        'audit_required': True
    },
    'healthcare': {
        'compliance': ['HIPAA', 'HITECH', 'FDA'],
        'security_level': 'high',
        'audit_required': True
    },
    'ecommerce': {
        'compliance': ['PCI-DSS', 'GDPR'],
        'security_level': 'medium',
        'audit_required': False
    }
}

# ============================================================================
# ANALYTICS CONFIGURATION
# ============================================================================

# Analytics Features
ANALYTICS_ENABLED = os.getenv('ANALYTICS_ENABLED', 'true').lower() == 'true'
PROJECT_INSIGHTS_ENABLED = os.getenv('PROJECT_INSIGHTS_ENABLED', 'true').lower() == 'true'
COMPLEXITY_ANALYSIS_ENABLED = os.getenv('COMPLEXITY_ANALYSIS_ENABLED', 'true').lower() == 'true'
RISK_ASSESSMENT_ENABLED = os.getenv('RISK_ASSESSMENT_ENABLED', 'true').lower() == 'true'

# Metrics Configuration
METRICS_RETENTION_DAYS = int(os.getenv('METRICS_RETENTION_DAYS', 90))
PERFORMANCE_MONITORING_ENABLED = os.getenv('PERFORMANCE_MONITORING_ENABLED', 'true').lower() == 'true'

# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================

# Environment Configuration
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development, staging, production
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# Server Configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
WORKERS = int(os.getenv('WORKERS', 4))

# Docker Configuration
DOCKER_ENABLED = os.getenv('DOCKER_ENABLED', 'false').lower() == 'true'
DOCKER_IMAGE_TAG = os.getenv('DOCKER_IMAGE_TAG', 'latest')

# ============================================================================
# FEATURE FLAGS
# ============================================================================

# Advanced Features
LANGCHAIN_ENABLED = os.getenv('LANGCHAIN_ENABLED', 'true').lower() == 'true'
ONEDRIVE_ENABLED = False  # Removed
TEMPLATE_SYSTEM_ENABLED = os.getenv('TEMPLATE_SYSTEM_ENABLED', 'true').lower() == 'true'
ANALYTICS_DASHBOARD_ENABLED = os.getenv('ANALYTICS_DASHBOARD_ENABLED', 'true').lower() == 'true'

# Experimental Features
EXPERIMENTAL_FEATURES_ENABLED = os.getenv('EXPERIMENTAL_FEATURES_ENABLED', 'false').lower() == 'true'
AI_AGENT_ENABLED = os.getenv('AI_AGENT_ENABLED', 'true').lower() == 'true'
MULTI_MODAL_PROCESSING_ENABLED = os.getenv('MULTI_MODAL_PROCESSING_ENABLED', 'true').lower() == 'true'

# ============================================================================
# VALIDATION AND SANITIZATION
# ============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Required configurations
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is required")
    
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    # Optional but recommended configurations
    if not OPENAI_API_KEY and LANGCHAIN_ENABLED:
        print("Warning: OPENAI_API_KEY not set - some LangChain features may be limited")
    
    if not REDIS_URL and MEMORY_TYPE == 'redis':
        errors.append("REDIS_URL is required when using Redis memory")
    
    
    # Validate numeric configurations
    if CHUNK_SIZE <= 0:
        errors.append("CHUNK_SIZE must be positive")
    
    if CHUNK_OVERLAP < 0:
        errors.append("CHUNK_OVERLAP must be non-negative")
    
    if TEMPERATURE < 0 or TEMPERATURE > 2:
        errors.append("TEMPERATURE must be between 0 and 2")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True

# ============================================================================
# CONFIGURATION HELPERS
# ============================================================================

def get_feature_config(feature_name: str) -> Dict:
    """Get configuration for a specific feature"""
    feature_configs = {
        'langchain': {
            'enabled': LANGCHAIN_ENABLED,
            'tracing': LANGCHAIN_TRACING_V2,
            'endpoint': LANGCHAIN_ENDPOINT,
            'project': LANGCHAIN_PROJECT
        },
        'analytics': {
            'enabled': ANALYTICS_ENABLED,
            'project_insights': PROJECT_INSIGHTS_ENABLED,
            'complexity_analysis': COMPLEXITY_ANALYSIS_ENABLED,
            'risk_assessment': RISK_ASSESSMENT_ENABLED
        },
        'templates': {
            'enabled': TEMPLATE_SYSTEM_ENABLED,
            'custom_enabled': CUSTOM_TEMPLATES_ENABLED,
            'directory': TEMPLATES_DIR
        }
    }
    
    return feature_configs.get(feature_name, {})

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    feature_flags = {
        'langchain': LANGCHAIN_ENABLED,
        'templates': TEMPLATE_SYSTEM_ENABLED,
        'analytics': ANALYTICS_ENABLED,
        'pinecone': PINECONE_ENABLED,
        'caching': CACHE_ENABLED,
        'rate_limiting': RATE_LIMIT_ENABLED,
        'image_processing': IMAGE_PROCESSING_ENABLED,
        'experimental': EXPERIMENTAL_FEATURES_ENABLED
    }
    
    return feature_flags.get(feature_name, False)

# Validate configuration on import
try:
    validate_config()
    print("✅ Configuration validated successfully")
except ValueError as e:
    print(f"⚠️ Configuration validation warning: {e}")

# Debug: Print key configuration values
if DEBUG:
    print(f"🔧 Environment: {ENVIRONMENT}")
    print(f"🔧 LangChain Enabled: {LANGCHAIN_ENABLED}")
    print(f"🔧 Analytics Enabled: {ANALYTICS_ENABLED}")
    print(f"🔧 Templates Enabled: {TEMPLATE_SYSTEM_ENABLED}")
    print(f"🔧 Pinecone Enabled: {PINECONE_ENABLED}")
