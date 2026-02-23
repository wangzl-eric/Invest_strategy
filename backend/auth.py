"""Authentication and authorization utilities."""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserAccount, UserRole, Role, APIKey

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str]:
    """Generate a new API key and return (key, hash, prefix)."""
    key = f"ibkr_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(key)
    key_prefix = key[:8]
    return key, key_hash, key_prefix


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_user_from_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user from API key."""
    if api_key is None:
        return None
    
    api_key_hash = hash_api_key(api_key)
    api_key_obj = db.query(APIKey).filter(
        APIKey.key_hash == api_key_hash,
        APIKey.is_active == True
    ).first()
    
    if api_key_obj is None:
        return None
    
    # Check expiration
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
        return None
    
    # Update last used
    api_key_obj.last_used_at = datetime.utcnow()
    db.commit()
    
    user = db.query(User).filter(User.id == api_key_obj.user_id).first()
    if user is None or not user.is_active:
        return None
    
    return user


async def get_current_user_or_api_key(
    user: Optional[User] = Depends(get_current_user_optional),
    api_user: Optional[User] = Depends(get_user_from_api_key),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from either JWT token or API key."""
    return user or api_user


def require_role(required_roles: List[str]):
    """Dependency to require specific roles."""
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Superusers have all permissions
        if current_user.is_superuser:
            return current_user
        
        # Get user roles
        user_roles = db.query(Role.name).join(UserRole).filter(
            UserRole.user_id == current_user.id
        ).all()
        user_role_names = [role[0] for role in user_roles]
        
        # Check if user has any required role
        if not any(role in user_role_names for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of these roles: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """Dependency to require a specific permission."""
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Superusers have all permissions
        if current_user.is_superuser:
            return current_user
        
        # Get user roles with permissions
        roles = db.query(Role).join(UserRole).filter(
            UserRole.user_id == current_user.id
        ).all()
        
        # Check if any role has the permission
        has_permission = False
        for role in roles:
            # Parse permissions JSON (simplified - in production use proper JSON parsing)
            permissions = getattr(role, 'permissions_json', '{}')
            # This is a simplified check - in production, properly parse JSON
            if permission in permissions or '*' in permissions:
                has_permission = True
                break
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires permission: {permission}"
            )
        
        return current_user
    
    return permission_checker


def get_user_accounts(user: User, db: Session) -> List[UserAccount]:
    """Get all accounts for a user."""
    return db.query(UserAccount).filter(
        UserAccount.user_id == user.id,
        UserAccount.is_active == True
    ).all()


def get_user_primary_account(user: User, db: Session) -> Optional[UserAccount]:
    """Get the primary account for a user."""
    return db.query(UserAccount).filter(
        UserAccount.user_id == user.id,
        UserAccount.is_primary == True,
        UserAccount.is_active == True
    ).first()
