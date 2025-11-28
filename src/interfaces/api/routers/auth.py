"""
Authentication router for login/register with JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.interfaces.api.dto.auth_dto import UserLogin, UserRegister, Token, TokenData, SetPassword
from src.interfaces.api.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from src.infrastructure.database import get_db
from src.infrastructure.repositories import SqlAlchemyUserRepository
from src.domain.models import User
from src.interfaces.api.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username and password to get JWT tokens."""
    user_repo = SqlAlchemyUserRepository(db)
    
    # Get user by username
    user = user_repo.get_by_username(form_data.username)
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/refresh", response_model=Token)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    token_data = decode_token(refresh_token)
    
    # Verify it's a refresh token
    if token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Create new access token
    user_repo = SqlAlchemyUserRepository(db)
    user = user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    access_token = create_access_token(data={"sub": user.id, "username": user.username})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/set-password", response_model=Token)
async def set_password(
    password_data: SetPassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allow Telegram users to set a password for web login.
    
    This endpoint is for users who registered via Telegram bot and want to
    access the web admin panel. Requires Telegram authentication (X-User-Id header).
    """
    user_repo = SqlAlchemyUserRepository(db)
    
    # Check if user already has a password
    if current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a password set. Use password reset instead."
        )
    
    # Check if email is already taken (if provided)
    if password_data.email:
        existing_email = user_repo.get_by_email(password_data.email)
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another user"
            )
    
    # Update user with password and email
    current_user.password_hash = get_password_hash(password_data.password)
    if password_data.email:
        current_user.email = password_data.email
    
    user_repo.update(current_user)
    
    # Create tokens for immediate web access
    access_token = create_access_token(data={"sub": current_user.id, "username": current_user.username})
    refresh_token = create_refresh_token(data={"sub": current_user.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)
