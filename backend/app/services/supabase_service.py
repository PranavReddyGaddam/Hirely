"""
Supabase database service for CRUD operations and authentication.
"""
import asyncio
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from app.core.config import settings
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.interview import InterviewResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseService:
    """Service for Supabase database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase credentials not configured")
            self.client: Optional[Client] = None
        else:
            self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    # -----------------------
    # Auth methods
    # -----------------------
    async def sign_up(self, email: str, password: str, full_name: str) -> Optional[Dict[str, Any]]:
        """
        Sign up a user with Supabase Auth and create a profile row.
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        try:
            # Supabase Auth sign up
            auth_resp = self.client.auth.sign_up({"email": email, "password": password})
            supa_user = auth_resp.user
            if not supa_user:
                logger.error("Supabase sign_up returned no user")
                return None
            # Rely on DB trigger to create profile row in public.users
            # (see supabase_schema.sql: trigger on auth.users → public.handle_new_user)
            return {"id": supa_user.id, "email": email, "full_name": full_name, "is_active": True}
        except Exception as e:
            logger.error(f"Supabase sign_up error: {e}")
            return None

    async def sign_in_with_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Sign in a user and return session/token payload."""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        try:
            auth_resp = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if not auth_resp or not auth_resp.session:
                return None
            return {
                "access_token": auth_resp.session.access_token,
                "refresh_token": auth_resp.session.refresh_token,
                "user": auth_resp.user
            }
        except Exception as e:
            logger.error(f"Supabase sign_in error: {e}")
            return None

    async def get_user_from_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Validate a Supabase JWT and return the auth user dict."""
        try:
            import jwt
            import json
            
            logger.info(f"Attempting to decode JWT token: {access_token[:50]}...")
            
            # Decode JWT without verification (since we trust Supabase)
            # In production, you should verify the signature
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            
            logger.info(f"JWT decoded successfully: {decoded_token}")
            
            # Extract user information from the token
            user_id = decoded_token.get("sub")
            email = decoded_token.get("email")
            
            if not user_id or not email:
                logger.error("Invalid token: missing user_id or email")
                return None
                
            result = {
                "id": user_id,
                "email": email,
                "user_metadata": decoded_token.get("user_metadata", {}),
                "app_metadata": decoded_token.get("app_metadata", {})
            }
            
            logger.info(f"Returning user data: {result}")
            return result
            
        except Exception as e:
            logger.error(f"JWT decode error: {e}")
            return None

    async def send_password_reset_email(self, email: str, redirect_to: Optional[str] = None) -> bool:
        """Send a password reset email using Supabase Auth."""
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
        try:
            # supabase-py v2 API
            if redirect_to:
                self.client.auth.reset_password_email(email, options={"redirect_to": redirect_to})
            else:
                self.client.auth.reset_password_email(email)
            logger.info(f"Password reset email requested for: {email}")
            return True
        except Exception as e:
            logger.error(f"Supabase password reset error: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID from Supabase.
        
        Args:
            user_id: User ID to fetch
            
        Returns:
            UserResponse: User data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # TODO: SUPABASE - Implement actual database query
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if response.data:
                user_data = response.data[0]
                return UserResponse(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """
        Get user by email from Supabase.
        
        Args:
            email: User email to fetch
            
        Returns:
            UserResponse: User data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # TODO: SUPABASE - Implement actual database query
            response = self.client.table("users").select("*").eq("email", email).execute()
            
            if response.data:
                user_data = response.data[0]
                return UserResponse(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            return None
    
    async def create_user_profile(self, user_id: str, email: str, full_name: str, access_token: str = None) -> Optional[UserResponse]:
        """
        Create a user profile in the public.users table.
        
        Args:
            user_id: User ID from auth.users
            email: User email
            full_name: User full name
            access_token: User's access token for RLS
            
        Returns:
            UserResponse: Created user data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # Create a client with the user's token for RLS
            if access_token:
                from supabase import create_client
                user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                user_client.auth.set_session(access_token, "")
                
                # Use upsert instead of insert to handle RLS better
                response = user_client.table("users").upsert({
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "is_active": True
                }).execute()
            else:
                # Fallback to regular client
                response = self.client.table("users").upsert({
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "is_active": True
                }).execute()
            
            if response.data:
                user_data = response.data[0]
                logger.info(f"User profile created successfully: {email}")
                return UserResponse(**user_data)
            return None
            
        except Exception as e:
            logger.error(f"Error creating user profile for {email}: {e}")
            return None
    
    async def upsert_profile(self, profile_data: Dict[str, Any]) -> Optional[UserResponse]:
        """Create or update a user profile row in the `users` table."""
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        try:
            response = self.client.table("users").upsert(profile_data).execute()
            if response.data:
                return UserResponse(**response.data[0])
            return None
        except Exception as e:
            logger.error(f"Error upserting profile: {e}")
            return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Update user data in Supabase.
        
        Args:
            user_id: User ID to update
            user_data: Updated user data
            
        Returns:
            UserResponse: Updated user data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # TODO: SUPABASE - Implement actual user update
            update_data = user_data.dict(exclude_unset=True)
            response = self.client.table("users").update(update_data).eq("id", user_id).execute()
            
            if response.data:
                return UserResponse(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user from Supabase.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            # TODO: SUPABASE - Implement actual user deletion
            response = self.client.table("users").delete().eq("id", user_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def get_user_interviews(self, user_id: str, skip: int = 0, limit: int = 100) -> List[InterviewResponse]:
        """
        Get user's interviews from Supabase.
        
        Args:
            user_id: User ID to fetch interviews for
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[InterviewResponse]: List of user interviews
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []
            
        try:
            # TODO: SUPABASE - Implement actual interview query
            response = self.client.table("interviews").select("*").eq("user_id", user_id).range(skip, skip + limit - 1).execute()
            
            interviews = []
            for interview_data in response.data:
                interviews.append(InterviewResponse(**interview_data))
            
            return interviews
            
        except Exception as e:
            logger.error(f"Error fetching interviews for user {user_id}: {e}")
            return []
    
    async def create_interview(self, interview_data: Dict[str, Any], access_token: str = None) -> Optional[InterviewResponse]:
        """
        Create a new interview in Supabase.
        
        Args:
            interview_data: Interview data to create
            access_token: User's access token for RLS
            
        Returns:
            InterviewResponse: Created interview data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # Use authenticated client for RLS
            if access_token:
                from supabase import create_client
                user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                user_client.auth.set_session(access_token, "")
                response = user_client.table("interviews").insert(interview_data).execute()
            else:
                # Fallback to regular client
                response = self.client.table("interviews").insert(interview_data).execute()
            
            if response.data:
                return InterviewResponse(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error creating interview: {e}")
            return None
    
    async def get_interview(self, interview_id: str, user_id: str) -> Optional[InterviewResponse]:
        """
        Get interview by ID from Supabase.
        
        Args:
            interview_id: Interview ID to fetch
            user_id: User ID for authorization
            
        Returns:
            InterviewResponse: Interview data or None if not found
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # Get interview with questions and responses
            response = self.client.table("interviews").select("""
                *,
                questions(*),
                responses(*)
            """).eq("id", interview_id).eq("user_id", user_id).execute()
            
            if response.data:
                interview_data = response.data[0]
                # Convert questions and responses to proper format
                interview_data['questions'] = interview_data.get('questions', [])
                interview_data['responses'] = interview_data.get('responses', [])
                return InterviewResponse(**interview_data)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching interview {interview_id}: {e}")
            return None
    
    async def update_interview(self, interview_id: str, interview_data: Dict[str, Any]) -> Optional[InterviewResponse]:
        """
        Update interview data in Supabase.
        
        Args:
            interview_id: Interview ID to update
            interview_data: Updated interview data
            
        Returns:
            InterviewResponse: Updated interview data or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            # TODO: SUPABASE - Implement actual interview update
            response = self.client.table("interviews").update(interview_data).eq("id", interview_id).execute()
            
            if response.data:
                return InterviewResponse(**response.data[0])
            return None
            
        except Exception as e:
            logger.error(f"Error updating interview {interview_id}: {e}")
            return None
    
    async def delete_interview(self, interview_id: str, user_id: str) -> bool:
        """
        Delete interview from Supabase.
        
        Args:
            interview_id: Interview ID to delete
            user_id: User ID for authorization
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            # TODO: SUPABASE - Implement actual interview deletion
            response = self.client.table("interviews").delete().eq("id", interview_id).eq("user_id", user_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting interview {interview_id}: {e}")
            return False
    
    async def create_question(self, question_data: Dict[str, Any]) -> bool:
        """
        Create a new question in Supabase.
        
        Args:
            question_data: Question data to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            response = self.client.table("questions").insert(question_data).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Successfully created question: {question_data.get('id', 'unknown')}")
                return True
            else:
                logger.error(f"Failed to create question - no data returned: {response}")
                return False
            
        except Exception as e:
            logger.error(f"Error creating question: {e}")
            return False
    
    async def create_response(self, response_data: Dict[str, Any]) -> bool:
        """
        Create a new response in Supabase.
        
        Args:
            response_data: Response data to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            response = self.client.table("responses").insert(response_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error creating response: {e}")
            return False
