"""Authentication and user management routes."""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, UserAccount, UserPreferences, APIKey, Role, UserRole
from backend.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    generate_api_key,
    hash_api_key,
    get_user_accounts,
    get_user_primary_account,
    security,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserAccountCreate(BaseModel):
    account_id: str
    account_name: Optional[str] = None
    is_primary: bool = False


class UserAccountResponse(BaseModel):
    id: int
    account_id: str
    account_name: Optional[str]
    is_primary: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class APIKeyCreate(BaseModel):
    key_name: str
    expires_in_days: Optional[int] = None  # None = no expiration


class APIKeyResponse(BaseModel):
    id: int
    key_name: str
    key_prefix: str
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    # Only include the full key on creation
    key: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    db.flush()
    
    # Create default preferences
    preferences = UserPreferences(user_id=user.id)
    db.add(preferences)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"New user registered: {user.username} ({user.email})")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1440,  # 24 hours in minutes
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("/me/accounts", response_model=List[UserAccountResponse])
async def get_my_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts for the current user."""
    accounts = get_user_accounts(current_user, db)
    return accounts


@router.post("/me/accounts", response_model=UserAccountResponse, status_code=status.HTTP_201_CREATED)
async def add_account(
    account_data: UserAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an IBKR account to the current user."""
    # Check if account already exists for this user
    existing = db.query(UserAccount).filter(
        UserAccount.user_id == current_user.id,
        UserAccount.account_id == account_data.account_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already added"
        )
    
    # If this is set as primary, unset other primary accounts
    if account_data.is_primary:
        db.query(UserAccount).filter(
            UserAccount.user_id == current_user.id,
            UserAccount.is_primary == True
        ).update({"is_primary": False})
    
    # Create account
    account = UserAccount(
        user_id=current_user.id,
        account_id=account_data.account_id,
        account_name=account_data.account_name or account_data.account_id,
        is_primary=account_data.is_primary,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    
    logger.info(f"User {current_user.username} added account: {account_data.account_id}")
    return account


@router.post("/me/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key for the current user."""
    key, key_hash, key_prefix = generate_api_key()
    
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    api_key = APIKey(
        user_id=current_user.id,
        key_name=key_data.key_name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        expires_at=expires_at,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    # Return the full key only on creation
    response = APIKeyResponse(
        id=api_key.id,
        key_name=api_key.key_name,
        key_prefix=api_key.key_prefix,
        is_active=api_key.is_active,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        key=key,  # Only time the full key is returned
    )
    
    logger.info(f"User {current_user.username} created API key: {key_data.key_name}")
    return response


@router.get("/me/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all API keys for the current user."""
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return keys


@router.delete("/me/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    logger.info(f"User {current_user.username} deleted API key: {api_key.key_name}")
