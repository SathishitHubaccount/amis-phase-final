"""
AMIS Authentication Module
JWT-based authentication with role-based access control (RBAC)
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib  # Using SHA-256 instead of bcrypt for Python 3.13 compatibility
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configuration
SECRET_KEY = "amis-secret-key-change-in-production-2026"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# ============================================================================
# MODELS
# ============================================================================

class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: str  # admin, manager, operator, viewer
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ============================================================================
# PASSWORD HASHING
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its SHA-256 hash"""
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password: str) -> str:
    """Generate SHA-256 password hash"""
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================================
# JWT TOKEN OPERATIONS
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ============================================================================
# USER AUTHENTICATION
# ============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    from database import get_user  # Import here to avoid circular dependency

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception

    return User(**user)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get current active (non-disabled) user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ============================================================================
# ROLE-BASED AUTHORIZATION
# ============================================================================

def require_role(required_roles: list):
    """
    Dependency to enforce role-based access control
    Usage: current_user = Depends(require_role(["admin", "manager"]))
    """
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker
