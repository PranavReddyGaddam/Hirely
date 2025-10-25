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
            # For now, use the service role key to bypass RLS
            # The service role key should have full access to all tables
            logger.info(f"Creating interview with service role key (bypassing RLS)")
            logger.info(f"Interview data: {interview_data}")
            
            # Use the service client which should bypass RLS
            response = self.client.table("interviews").insert(interview_data).execute()
            logger.info(f"Interview insert response: {response.data if response.data else 'No data'}")
            
            if response.data:
                logger.info(f"Interview created successfully: {response.data[0]['id']}")
                return InterviewResponse(**response.data[0])
            else:
                logger.error(f"No data returned from interview insert: {response}")
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
            logger.info(f"[Supabase] Fetching interview {interview_id} for user {user_id}")
            # Get interview with questions and responses
            response = self.client.table("interviews").select("""
                *,
                questions(*),
                responses(*)
            """).eq("id", interview_id).eq("user_id", user_id).execute()
            
            logger.info(f"[Supabase] Query response: {len(response.data) if response.data else 0} results")
            
            if response.data:
                interview_data = response.data[0]
                logger.info(f"[Supabase] Interview found: {interview_data.get('title')}")
                # Convert questions and responses to proper format
                interview_data['questions'] = interview_data.get('questions', [])
                interview_data['responses'] = interview_data.get('responses', [])
                return InterviewResponse(**interview_data)
            
            logger.warning(f"[Supabase] Interview {interview_id} not found for user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching interview {interview_id}: {e}", exc_info=True)
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
    
    # System Design methods
    async def insert_screenshot(self, screenshot_data: Dict[str, Any]) -> bool:
        """
        Insert screenshot data into the screenshots table.
        
        Args:
            screenshot_data: Screenshot data to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            response = self.client.table("screenshots").insert(screenshot_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting screenshot: {e}")
            return False
    
    async def insert_progress(self, progress_data: Dict[str, Any]) -> bool:
        """
        Insert progress data into the progress table.
        
        Args:
            progress_data: Progress data to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            response = self.client.table("progress").insert(progress_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting progress: {e}")
            return False
    
    async def insert_chat_message(self, chat_data: Dict[str, Any]) -> bool:
        """
        Insert chat message into the chat_messages table.
        
        Args:
            chat_data: Chat message data to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            response = self.client.table("chat_messages").insert(chat_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting chat message: {e}")
            return False
    
    async def get_recent_progress(self, interview_id: str, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Get recent progress data for an interview and question.
        
        Args:
            interview_id: Interview ID
            question_id: Question ID
            
        Returns:
            Optional[Dict[str, Any]]: Recent progress data or None
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            response = self.client.table("progress").select("*").eq("interview_id", interview_id).eq("question_id", question_id).order("created_at", desc=True).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting recent progress: {e}")
            return None
    
    # -----------------------
    # Storage methods for video files
    # -----------------------
    async def upload_interview_video(
        self, 
        user_id: str, 
        interview_id: str, 
        video_data: bytes, 
        file_extension: str = "webm"
    ) -> Optional[Dict[str, Any]]:
        """
        Upload interview video to Supabase Storage (object storage).
        
        Args:
            user_id: User ID (used for folder organization)
            interview_id: Interview ID
            video_data: Video file bytes
            file_extension: File extension (webm, mp4, etc.)
            
        Returns:
            Dict with storage_path and public_url, or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            import time
            timestamp = int(time.time())
            
            # Storage path: user_id/interview_id_timestamp.webm
            storage_path = f"{user_id}/{interview_id}_{timestamp}.{file_extension}"
            
            logger.info(f"Uploading video to storage: {storage_path}")
            logger.info(f"Video size: {len(video_data) / 1024 / 1024:.2f} MB")
            
            # Upload to Supabase Storage bucket
            response = self.client.storage.from_("interview-videos").upload(
                path=storage_path,
                file=video_data,
                file_options={
                    "content-type": f"video/{file_extension}",
                    "cache-control": "3600",
                    "upsert": "true"  # Overwrite if exists
                }
            )
            
            logger.info(f"Upload response: {response}")
            
            # Get public URL (signed URL for private buckets)
            signed_url = self.client.storage.from_("interview-videos").create_signed_url(
                path=storage_path,
                expires_in=31536000  # 1 year expiry
            )
            
            if signed_url:
                public_url = signed_url.get('signedURL')
                logger.info(f"Video uploaded successfully: {storage_path}")
                
                return {
                    "storage_path": storage_path,
                    "public_url": public_url,
                    "size_bytes": len(video_data)
                }
            else:
                logger.error("Failed to generate signed URL")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading video to storage: {e}")
            return None
    
    async def get_video_signed_url(self, storage_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get a signed URL for accessing a video from Supabase Storage.
        
        Args:
            storage_path: Storage path (user_id/video_filename.webm)
            expires_in: URL expiry time in seconds (default 1 hour)
            
        Returns:
            Signed URL string or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            signed_url = self.client.storage.from_("interview-videos").create_signed_url(
                path=storage_path,
                expires_in=expires_in
            )
            
            if signed_url:
                return signed_url.get('signedURL')
            return None
            
        except Exception as e:
            logger.error(f"Error creating signed URL: {e}")
            return None
    
    async def download_video(self, storage_path: str) -> Optional[bytes]:
        """
        Download video bytes from Supabase Storage.
        
        Args:
            storage_path: Storage path (user_id/video_filename.webm)
            
        Returns:
            Video bytes or None if failed
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
        
        try:
            response = self.client.storage.from_("interview-videos").download(storage_path)
            
            if response:
                logger.info(f"Downloaded video from storage: {storage_path}")
                return response
            return None
            
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    async def delete_video(self, storage_path: str) -> bool:
        """
        Delete video from Supabase Storage.
        
        Args:
            storage_path: Storage path (user_id/video_filename.webm)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            response = self.client.storage.from_("interview-videos").remove([storage_path])
            logger.info(f"Deleted video from storage: {storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    async def update_interview_video_metadata(
        self,
        interview_id: str,
        storage_path: str,
        public_url: str,
        size_bytes: int
    ) -> bool:
        """
        Update interview record with video storage metadata.
        
        Args:
            interview_id: Interview ID
            storage_path: Storage path in Supabase
            public_url: Signed URL for accessing video
            size_bytes: Video file size
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            from datetime import datetime
            
            response = self.client.table("interviews").update({
                "video_storage_path": storage_path,
                "video_url": public_url,
                "video_size_bytes": size_bytes,
                "video_uploaded_at": datetime.utcnow().isoformat()
            }).eq("id", interview_id).execute()
            
            if response.data:
                logger.info(f"Updated interview {interview_id} with video metadata")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating interview video metadata: {e}")
            return False