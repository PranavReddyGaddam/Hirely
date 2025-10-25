from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/test")
async def test_endpoint():
    """Test endpoint without authentication"""
    return {"message": "Test endpoint working", "status": "success"}

@router.get("/test-auth")
async def test_auth_endpoint(request: Request):
    """Test endpoint with manual JWT decoding"""
    try:
        import jwt
        from datetime import datetime
        
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return {"error": "No valid authorization header"}
        
        token = authorization.split(" ")[1]
        
        # Decode JWT without verification
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        
        # Create a basic user object
        user_id = decoded_token.get("sub")
        email = decoded_token.get("email")
        full_name = decoded_token.get("user_metadata", {}).get("full_name", email.split("@")[0])
        current_time = datetime.utcnow()
        
        user_response = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "is_active": True,
            "created_at": current_time.isoformat(),
            "updated_at": current_time.isoformat()
        }
        
        return {
            "message": "JWT decoded successfully",
            "user": user_response
        }
    except Exception as e:
        return {"error": f"JWT decode failed: {str(e)}"}

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_user)
):
    """Update current user information"""
    user_service = UserService()
    try:
        updated_user = await user_service.update_user(current_user.id, user_update)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/me")
async def delete_current_user(current_user = Depends(get_current_user)):
    """Delete current user account"""
    user_service = UserService()
    try:
        await user_service.delete_user(current_user.id)
        return {"message": "User account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
