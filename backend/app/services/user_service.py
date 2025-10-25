"""
User service for profile management and user operations.
"""
from typing import Optional
from app.schemas.user import UserResponse, UserUpdate
from app.services.supabase_service import SupabaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user profile operations."""
    
    def __init__(self):
        """Initialize user service."""
        self.supabase_service = SupabaseService()
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID to fetch
            
        Returns:
            UserResponse: User data or None if not found
        """
        return await self.supabase_service.get_user_by_id(user_id)
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserResponse]:
        """
        Update user profile.
        
        Args:
            user_id: User ID to update
            user_update: Updated user data
            
        Returns:
            UserResponse: Updated user data or None if failed
        """
        # Check if user exists
        existing_user = await self.supabase_service.get_user_by_id(user_id)
        if not existing_user:
            raise Exception("User not found")
        
        # Update user data
        updated_user = await self.supabase_service.update_user(user_id, user_update)
        
        if updated_user:
            logger.info(f"User profile updated successfully: {user_id}")
            return updated_user
        
        raise Exception("Failed to update user profile")
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user account.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if user exists
        existing_user = await self.supabase_service.get_user_by_id(user_id)
        if not existing_user:
            raise Exception("User not found")
        
        # Delete user
        success = await self.supabase_service.delete_user(user_id)
        
        if success:
            logger.info(f"User account deleted successfully: {user_id}")
            return True
        
        raise Exception("Failed to delete user account")
    
    async def get_user_statistics(self, user_id: str) -> dict:
        """
        Get user interview statistics.
        
        Args:
            user_id: User ID to get statistics for
            
        Returns:
            dict: User statistics
        """
        # Get user interviews
        interviews = await self.supabase_service.get_user_interviews(user_id)
        
        # Calculate statistics
        total_interviews = len(interviews)
        completed_interviews = len([i for i in interviews if i.status == "completed"])
        
        # TODO: Add more detailed statistics (average scores, improvement trends, etc.)
        statistics = {
            "total_interviews": total_interviews,
            "completed_interviews": completed_interviews,
            "success_rate": completed_interviews / total_interviews if total_interviews > 0 else 0,
            "recent_activity": "last_week"  # Placeholder
        }
        
        logger.info(f"Retrieved statistics for user: {user_id}")
        return statistics
    
    async def update_user_preferences(self, user_id: str, preferences: dict) -> bool:
        """
        Update user preferences.
        
        Args:
            user_id: User ID to update preferences for
            preferences: User preferences data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # TODO: Implement user preferences storage
        # This could include interview types, difficulty levels, feedback preferences, etc.
        
        logger.info(f"User preferences updated for: {user_id}")
        return True
    
    async def get_user_achievements(self, user_id: str) -> list:
        """
        Get user achievements and badges.
        
        Args:
            user_id: User ID to get achievements for
            
        Returns:
            list: List of user achievements
        """
        # TODO: Implement achievement system
        # This could include badges for completing interviews, improving scores, etc.
        
        achievements = [
            {
                "id": "first_interview",
                "name": "First Interview",
                "description": "Completed your first interview",
                "earned_at": "2024-01-01T00:00:00Z",
                "icon": "🎯"
            }
        ]
        
        logger.info(f"Retrieved achievements for user: {user_id}")
        return achievements
