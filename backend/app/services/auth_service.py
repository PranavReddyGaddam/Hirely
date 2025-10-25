"""
Authentication service for user registration and login using Supabase Auth.
"""
from typing import Optional
from app.core.config import settings
from app.schemas.auth import UserCreate, UserResponse, Token
from app.services.supabase_service import SupabaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.supabase_service = SupabaseService()
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user account.
        
        Args:
            user_data: User registration data
            
        Returns:
            UserResponse: Created user data
            
        Raises:
            Exception: If user creation fails
        """
        # Sign up in Supabase Auth and upsert profile
        result = await self.supabase_service.sign_up(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        if not result:
            raise Exception("Failed to create user account")
        # Fetch full profile
        profile = await self.supabase_service.get_user_by_id(result["id"])  # type: ignore
        if not profile:
            raise Exception("Failed to fetch created user profile")
        logger.info(f"User created successfully: {profile.email}")
        return profile
    
    async def authenticate_user(self, email: str, password: str) -> Token:
        """
        Authenticate user and return access token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Token: Access token data
            
        Raises:
            Exception: If authentication fails
        """
        # Authenticate via Supabase Auth
        session = await self.supabase_service.sign_in_with_password(email, password)
        if not session:
            raise Exception("Invalid email or password")
        access_token = session["access_token"]
        
        # Get profile - if it doesn't exist, create it
        user = await self.supabase_service.get_user_by_email(email)
        if not user:
            # Try to create the profile manually if it doesn't exist
            auth_user = session.get("user")
            if auth_user:
                user_id = auth_user.get("id")
                full_name = auth_user.get("user_metadata", {}).get("full_name", email.split("@")[0])
                
                # Create user profile manually
                created_user = await self.supabase_service.create_user_profile(
                    user_id=user_id,
                    email=email,
                    full_name=full_name,
                    access_token=access_token
                )
                if created_user:
                    user = created_user
                else:
                    raise Exception("Failed to create user profile")
            else:
                raise Exception("Failed to load user profile")
        
        logger.info(f"User authenticated successfully: {email}")
        return Token(access_token=access_token, token_type="bearer", expires_in=60 * settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    async def reset_password(self, email: str) -> bool:
        """
        Initiate password reset process.
        
        Args:
            email: User email
            
        Returns:
            bool: True if reset email sent, False otherwise
        """
        success = await self.supabase_service.send_password_reset_email(email)
        return success
    
    async def verify_email(self, token: str) -> bool:
        """
        Verify user email with token.
        
        Args:
            token: Email verification token
            
        Returns:
            bool: True if verification successful, False otherwise
        """
        # TODO: SUPABASE - Verify email token with Supabase Auth
        logger.info(f"Email verification attempted with token: {token[:10]}...")
        return True
    
    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed successfully, False otherwise
        """
        try:
            # For now, we'll use Supabase's update_user method
            # In a real implementation, you'd verify the old password first
            if not self.client:
                logger.error("Supabase client not initialized")
                return False
            
            # Update user password using Supabase Auth
            response = self.client.auth.update_user({
                "password": new_password
            })
            
            if response.user:
                logger.info(f"Password changed successfully for user: {user_id}")
                return True
            else:
                logger.error(f"Failed to change password for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            return False
