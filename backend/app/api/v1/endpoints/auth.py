from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from app.schemas.auth import Token, UserCreate, UserResponse
from app.services.auth_service import AuthService
from app.core.auth import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    auth_service = AuthService()
    try:
        user = await auth_service.create_user(user_data)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Login user and return access token"""
    auth_service = AuthService()
    try:
        token = await auth_service.authenticate_user(login_data.email, login_data.password)
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Successfully logged out"}


class PasswordResetRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(payload: PasswordResetRequest):
    """Request a password reset email via Supabase."""
    auth_service = AuthService()
    try:
        success = await auth_service.reset_password(payload.email)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to send reset email")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user = Depends(get_current_user)
):
    """Change user password."""
    auth_service = AuthService()
    try:
        success = await auth_service.change_password(
            user_id=current_user.id,
            old_password=payload.current_password,
            new_password=payload.new_password
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to change password")
        return {"message": "Password changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
