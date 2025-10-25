"""
ElevenLabs API endpoints for managing conversational AI agents
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from app.services.elevenlabs_service import ElevenLabsService
from app.core.auth import get_current_user

router = APIRouter()

# Pydantic models for request/response
class PersonaData(BaseModel):
    id: str
    name: str
    title: str
    location: str
    bio: str
    expertise: list[str]
    experience: str
    industry: str
    insights: Optional[list[str]] = None

class CreateAgentRequest(BaseModel):
    persona: PersonaData
    startup_idea: Optional[str] = None
    previous_analysis: Optional[Dict[str, Any]] = None
    interview_config: Optional[Dict[str, Any]] = None

class StartConversationRequest(BaseModel):
    agent_id: str
    startup_idea: Optional[str] = None
    previous_analysis: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent_id: str
    persona_id: str
    persona_name: str
    agent_url: str

class ConversationResponse(BaseModel):
    conversation_id: str
    agent_id: str
    context_provided: bool

@router.post("/create-agent", response_model=AgentResponse)
async def create_agent(
    request: CreateAgentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new ElevenLabs conversational AI agent for a specific persona
    """
    try:
        elevenlabs_service = ElevenLabsService()
        
        # Convert Pydantic model to dict
        persona_dict = request.persona.model_dump()
        
        # Create the agent
        agent_result = await elevenlabs_service.create_agent_for_persona(
            persona=persona_dict,
            startup_idea=request.startup_idea,
            previous_analysis=request.previous_analysis,
            interview_config=request.interview_config
        )
        
        # Get the agent link
        agent_link = await elevenlabs_service.get_agent_link(agent_result["agent_id"])
        
        return AgentResponse(
            agent_id=agent_result["agent_id"],
            persona_id=agent_result["persona_id"],
            persona_name=agent_result["persona_name"],
            agent_url=agent_link["agent_url"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start-conversation", response_model=ConversationResponse)
async def start_conversation(
    request: StartConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start a conversation with an existing ElevenLabs agent
    """
    try:
        elevenlabs_service = ElevenLabsService()
        
        conversation_result = await elevenlabs_service.start_conversation_with_context(
            agent_id=request.agent_id,
            startup_idea=request.startup_idea,
            previous_analysis=request.previous_analysis
        )
        
        return ConversationResponse(
            conversation_id=conversation_result["conversation_id"],
            agent_id=conversation_result["agent_id"],
            context_provided=conversation_result["context_provided"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{conversation_id}")
async def get_conversation_details(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details and transcript of a completed conversation
    """
    try:
        elevenlabs_service = ElevenLabsService()
        conversation_details = await elevenlabs_service.get_conversation_details(conversation_id)
        return conversation_details
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agent/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an ElevenLabs agent
    """
    try:
        elevenlabs_service = ElevenLabsService()
        success = await elevenlabs_service.delete_agent(agent_id)
        
        if success:
            return {"message": "Agent deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete agent")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/{agent_id}/link")
async def get_agent_link(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get the public link for an ElevenLabs agent
    """
    try:
        elevenlabs_service = ElevenLabsService()
        agent_link = await elevenlabs_service.get_agent_link(agent_id)
        return agent_link
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SendMessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    response: str
    timestamp: str

@router.post("/agent/{agent_id}/message", response_model=MessageResponse)
async def send_message_to_agent(
    agent_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to an ElevenLabs agent and get a response
    """
    try:
        elevenlabs_service = ElevenLabsService()
        response = await elevenlabs_service.send_message_to_agent(agent_id, request.message)
        return MessageResponse(
            response=response,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
