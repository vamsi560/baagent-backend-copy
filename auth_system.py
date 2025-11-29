# auth_system.py
# Authentication system for multi-user platform

import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from functools import wraps
from flask import request, jsonify, current_app
from database_multi_user import get_db, User, authenticate_user, create_user, UserRole

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

class AuthManager:
    """Authentication manager for the multi-user system"""
    
    def __init__(self):
        self.secret_key = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.expiration_hours = JWT_EXPIRATION_HOURS
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_token(self, user_id: str, email: str, role: str) -> str:
        """Create a JWT token for a user"""
        payload = {
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.expiration_hours),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from token"""
        payload = self.decode_token(token)
        if payload:
            db = next(get_db())
            try:
                user = db.query(User).filter(User.id == payload['user_id']).first()
                if user and user.is_active:
                    return {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'role': user.role,
                        'is_active': user.is_active
                    }
            finally:
                db.close()
        return None

# Global auth manager instance
auth_manager = AuthManager()

def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # Verify token and get user
        current_user = auth_manager.get_current_user(token)
        if not current_user:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        # Add user to request context
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated

def role_required(allowed_roles: list):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'message': 'Authentication required'}), 401
            
            user_role = request.current_user.get('role')
            if user_role not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def project_access_required(f):
    """Decorator to require project access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'message': 'Authentication required'}), 401
        
        project_id = kwargs.get('project_id') or request.json.get('project_id')
        if not project_id:
            return jsonify({'message': 'Project ID required'}), 400
        
        # Check if user has access to the project
        db = next(get_db())
        try:
            from database_multi_user import user_projects, Project
            
            # Check if user owns the project
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            
            user_id = request.current_user['id']
            
            # Owner has full access
            if project.owner_id == user_id:
                return f(*args, **kwargs)
            
            # Check if user is a member
            member = db.execute(
                user_projects.select().where(
                    user_projects.c.user_id == user_id,
                    user_projects.c.project_id == project_id
                )
            ).first()
            
            if not member:
                return jsonify({'message': 'Access denied to project'}), 403
            
            return f(*args, **kwargs)
            
        finally:
            db.close()
    
    return decorated

# Authentication API endpoints
def register_user():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        required_fields = ['email', 'name', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        email = data['email']
        name = data['name']
        password = data['password']
        role = data.get('role', UserRole.ANALYST)
        
        # Validate email format
        if '@' not in email:
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        db = next(get_db())
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                return jsonify({'message': 'User with this email already exists'}), 409
            
            # Create new user
            user = create_user(db, email, name, password, role)
            
            # Create token
            token = auth_manager.create_token(user.id, user.email, user.role)
            
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role
                },
                'token': token
            }), 201
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

def login_user():
    """Login user and return token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password required'}), 400
        
        db = next(get_db())
        try:
            # Authenticate user
            user = authenticate_user(db, email, password)
            
            if not user:
                return jsonify({'message': 'Invalid email or password'}), 401
            
            if not user.is_active:
                return jsonify({'message': 'Account is deactivated'}), 401
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.commit()
            
            # Create token
            token = auth_manager.create_token(user.id, user.email, user.role)
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                },
                'token': token
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

def get_user_profile():
    """Get current user profile"""
    try:
        current_user = request.current_user
        
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == current_user['id']).first()
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            return jsonify({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'preferences': user.preferences or {}
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get profile: {str(e)}'}), 500

def update_user_profile():
    """Update current user profile"""
    try:
        current_user = request.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == current_user['id']).first()
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            # Update allowed fields
            if 'name' in data:
                user.name = data['name']
            
            if 'preferences' in data:
                user.preferences = data['preferences']
            
            # Update password if provided
            if 'password' in data:
                if len(data['password']) < 6:
                    return jsonify({'message': 'Password must be at least 6 characters'}), 400
                user.password_hash = auth_manager.hash_password(data['password'])
            
            db.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'preferences': user.preferences or {}
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to update profile: {str(e)}'}), 500

def change_password():
    """Change user password"""
    try:
        current_user = request.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'message': 'Current and new password required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'message': 'New password must be at least 6 characters'}), 400
        
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == current_user['id']).first()
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            # Verify current password
            if not auth_manager.verify_password(current_password, user.password_hash):
                return jsonify({'message': 'Current password is incorrect'}), 401
            
            # Update password
            user.password_hash = auth_manager.hash_password(new_password)
            db.commit()
            
            return jsonify({'message': 'Password changed successfully'}), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to change password: {str(e)}'}), 500

def logout_user():
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Logout successful'}), 200

# Admin functions
@token_required
@role_required([UserRole.ADMIN])
def get_all_users():
    """Get all users (admin only)"""
    try:
        db = next(get_db())
        try:
            users = db.query(User).all()
            
            return jsonify({
                'users': [
                    {
                        'id': user.id,
                        'email': user.email,
                        'name': user.name,
                        'role': user.role,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat(),
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    }
                    for user in users
                ]
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to get users: {str(e)}'}), 500

@token_required
@role_required([UserRole.ADMIN])
def update_user_status():
    """Update user status (admin only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        is_active = data.get('is_active')
        role = data.get('role')
        
        if user_id is None:
            return jsonify({'message': 'User ID required'}), 400
        
        db = next(get_db())
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            # Update fields
            if is_active is not None:
                user.is_active = is_active
            
            if role:
                user.role = role
            
            db.commit()
            
            return jsonify({
                'message': 'User updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'is_active': user.is_active
                }
            }), 200
            
        finally:
            db.close()
            
    except Exception as e:
        return jsonify({'message': f'Failed to update user: {str(e)}'}), 500

# Test function
def test_auth_system():
    """Test the authentication system"""
    print("🧪 Testing Authentication System...")
    
    # Test password hashing
    password = "testpassword123"
    hashed = auth_manager.hash_password(password)
    print(f"✅ Password hashing: {len(hashed)} characters")
    
    # Test password verification
    is_valid = auth_manager.verify_password(password, hashed)
    print(f"✅ Password verification: {is_valid}")
    
    # Test token creation and decoding
    user_id = "test-user-id"
    email = "test@example.com"
    role = "analyst"
    
    token = auth_manager.create_token(user_id, email, role)
    print(f"✅ Token creation: {len(token)} characters")
    
    payload = auth_manager.decode_token(token)
    print(f"✅ Token decoding: {payload['email']} - {payload['role']}")
    
    return {
        'password_hashing': True,
        'password_verification': is_valid,
        'token_creation': len(token) > 0,
        'token_decoding': payload is not None
    }

if __name__ == "__main__":
    test_auth_system()
