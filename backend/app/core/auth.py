"""
Authentication utilities and dependencies for JWT token validation.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime
from app.core.config import settings
from app.schemas.auth import TokenData
from app.schemas.user import UserResponse, UserBase
from app.services.supabase_service import SupabaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_token_from_header(request: Request) -> str:
    """Extract token from Authorization header manually."""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    logger.info(f"Extracted token: {token[:50]}...")
    return token


async def get_current_user(token: str = Depends(get_token_from_header)) -> UserResponse:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        
    Returns:
        UserResponse: Current user data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Validate Supabase JWT and fetch user
    logger.info(f"Validating token: {token[:50]}...")
    supabase_service = SupabaseService()
    auth_user = await supabase_service.get_user_from_token(token)
    if not auth_user:
        logger.error("Failed to get user from token")
        raise credentials_exception
    
    logger.info(f"Auth user retrieved: {auth_user}")
    
    user_id = auth_user.get("id")
    email = auth_user.get("email")
    
    if not user_id or not email:
        raise credentials_exception
    
    # For now, just return a basic user object without database interaction
    # This bypasses the RLS policy issues
    full_name = auth_user.get("user_metadata", {}).get("full_name", email.split("@")[0])
    current_time = datetime.utcnow()
    
    # Create a basic user object with all required fields
    user = UserResponse(
        id=user_id,
        email=email,
        full_name=full_name,
        is_active=True,
        created_at=current_time,
        updated_at=current_time
    )
    
    logger.info(f"Returning basic user object: {user}")
        
    return user


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency to get the current active user.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        UserResponse: Current active user data
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def verify_token(token: str) -> Optional[TokenData]:
    """Validate Supabase JWT by querying Supabase and returning minimal token data."""
    try:
        supabase_service = SupabaseService()
        auth_user = asyncio.run(supabase_service.get_user_from_token(token))  # type: ignore
        if not auth_user:
            return None
        return TokenData(email=auth_user.get("email"), user_id=auth_user.get("id"))
    except Exception:
        return None
