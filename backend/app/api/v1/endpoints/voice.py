"""
Voice API Endpoints for VAPI testing
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import os
from dotenv import load_dotenv
from vapi import Vapi
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)
router = APIRouter()

# Initialize VAPI
vapi = Vapi(token=os.getenv("VAPI_KEY"))

@router.post("/create-call")
async def create_call(
    request: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a VAPI call"""
    try:
        phone_number = request.get("phone_number")
        
        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required")
        
        # Create assistant
        assistant = vapi.assistants.create(
            name="Interview Assistant",
            first_message="Hello! I'm your AI interview assistant. I'll be conducting your interview today. Are you ready to begin?",
            model={
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "messages": [{
                    "role": "system",
                    "content": "You are a professional interview assistant. Ask 2-3 simple questions about programming or problem-solving. Keep it brief and friendly."
                }]
            },
            voice={
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM"
            }
        )
        
        # Make the call
        logger.info(f"Creating call with assistant_id: {assistant.id}, phone_number: {phone_number}")
        
        # Use the phone_number_id from your VAPI account
        phone_number_id = "96651774-eb23-4ec4-844c-7e81fb658b8a"
        
        call = vapi.calls.create(
            assistant_id=assistant.id,
            phone_number_id=phone_number_id,
            customer={
                "number": phone_number
            }
        )
        
        return {
            "success": True,
            "call_id": call.id,
            "assistant_id": assistant.id,
            "phone_number": phone_number
        }
    
    except Exception as e:
        logger.error(f"Error creating call: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create call: {str(e)}")

@router.get("/call-status/{call_id}")
async def get_call_status(
    call_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get call status"""
    try:
        call = vapi.calls.get(call_id)
        
        return {
            "success": True,
            "call_id": call.id,
            "status": getattr(call, 'status', 'unknown')
        }
    
    except Exception as e:
        logger.error(f"Error getting call status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get call status: {str(e)}")
