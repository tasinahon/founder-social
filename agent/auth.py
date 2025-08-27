"""
User Authentication and Session Management
Handles user registration, login, and session management
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sqlite3
import jwt
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

security = HTTPBearer()

class UserManager:
    def __init__(self, db_path: str = "./data/users.db"):
        self.db_path = db_path
        self.ensure_db_exists()
    
    def ensure_db_exists(self):
        """Create the users database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                company TEXT,
                plan TEXT DEFAULT 'free',
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create user sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create API usage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash a password for storing"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, email: str, password: str, name: str = None, company: str = None) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return {'success': False, 'error': 'User already exists'}
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, name, company)
                VALUES (?, ?, ?, ?)
            ''', (email, password_hash, name, company))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True, 
                'user_id': user_id,
                'message': 'User created successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, password_hash, name, company, plan, is_active
                FROM users WHERE email = ? AND is_active = 1
            ''', (email,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return None
            
            user_id, email, password_hash, name, company, plan, is_active = user_row
            
            if not self.verify_password(password, password_hash):
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            
            return {
                'id': user_id,
                'email': email,
                'name': name,
                'company': company,
                'plan': plan
            }
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_session(self, user_id: int, user_agent: str = None, ip_address: str = None) -> str:
        """Create a new user session"""
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=30)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_sessions (user_id, session_token, expires_at, user_agent, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, user_agent, ip_address))
            
            conn.commit()
            conn.close()
            
            return session_token
        except Exception as e:
            print(f"Session creation error: {e}")
            return None
    
    def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, name, company, plan
                FROM users WHERE email = ? AND is_active = 1
            ''', (email,))
            
            user_row = cursor.fetchone()
            conn.close()
            
            if user_row:
                user_id, email, name, company, plan = user_row
                return {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'company': company,
                    'plan': plan
                }
            return None
        except jwt.PyJWTError:
            return None
    
    def get_user_from_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from session token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.email, u.name, u.company, u.plan
                FROM users u
                JOIN user_sessions s ON u.id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            
            user_row = cursor.fetchone()
            
            if user_row:
                # Update last used timestamp
                cursor.execute('''
                    UPDATE user_sessions SET last_used = CURRENT_TIMESTAMP
                    WHERE session_token = ?
                ''', (session_token,))
                conn.commit()
                
                user_id, email, name, company, plan = user_row
                conn.close()
                return {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'company': company,
                    'plan': plan
                }
            
            conn.close()
            return None
        except Exception as e:
            print(f"Session validation error: {e}")
            return None
    
    def track_api_usage(self, user_id: int, platform: str, action: str, success: bool = True):
        """Track API usage for rate limiting and analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_usage (user_id, platform, action, success)
                VALUES (?, ?, ?, ?)
            ''', (user_id, platform, action, success))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"API usage tracking error: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total posts published
            cursor.execute('''
                SELECT platform, COUNT(*) as count
                FROM api_usage 
                WHERE user_id = ? AND action = 'publish' AND success = 1
                GROUP BY platform
            ''', (user_id,))
            
            platform_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get total usage this month
            cursor.execute('''
                SELECT COUNT(*) as monthly_usage
                FROM api_usage 
                WHERE user_id = ? AND action = 'publish' AND success = 1
                AND timestamp >= date('now', 'start of month')
            ''', (user_id,))
            
            monthly_usage = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'platform_stats': platform_stats,
                'monthly_usage': monthly_usage,
                'total_posts': sum(platform_stats.values())
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {'platform_stats': {}, 'monthly_usage': 0, 'total_posts': 0}

# Global instance
user_manager = UserManager()

# Dependency to get current user
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Try Authorization header first
        authorization = request.headers.get("Authorization")
        token = None
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            # Try cookie fallback
            token = request.cookies.get("access_token")
        
        if not token:
            raise credentials_exception
        
        # Try JWT token first
        user = user_manager.get_user_from_token(token)
        if user:
            return user
        
        # Try session token
        user = user_manager.get_user_from_session(token)
        if user:
            return user
        
        raise credentials_exception
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

# Optional dependency (for public endpoints)
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get the current user if authenticated, otherwise None"""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
