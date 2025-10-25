# VAPI Integration Guide

## Overview
This guide explains how to use the VAPI integration for voice-based interviews in the Hirely platform.

## Setup

### 1. Environment Variables
Add your VAPI API key to your environment:
```bash
export VAPI_KEY="your_vapi_api_key_here"
```

### 2. Install Dependencies
```bash
pip install vapi-python==1.0.0
```

## Files Created

### 1. Test Script: `test_vapi_integration.py`
Interactive test script for VAPI functionality:
- Create interview assistants
- Create sales assistants  
- Make test calls
- Check call status
- List and manage assistants

### 2. Voice Test API: `app/api/v1/endpoints/voice_test.py`
Simple FastAPI endpoints for testing VAPI:
- Test connection
- Create assistants
- Make calls
- Check call status
- List assistants

## Usage

### Running the Test Script
```bash
cd backend
python test_vapi_integration.py
```

### Voice Test Endpoints
- `GET /api/v1/voice/test-connection` - Test VAPI connection
- `POST /api/v1/voice/create-assistant` - Create a new assistant
- `GET /api/v1/voice/assistants` - List all assistants
- `POST /api/v1/voice/make-call` - Make a test call
- `GET /api/v1/voice/calls/{call_id}/status` - Get call status
- `GET /api/v1/voice/health` - Health check

### Creating an Assistant
```python
import vapi

# Set your API key
vapi.api_key = "your_vapi_api_key"

# Create an interview assistant
assistant = vapi.assistants.create(
    name="Interview Assistant",
    first_message="Hello! I'm your AI interview assistant.",
    model={
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.7,
        "messages": [{
            "role": "system",
            "content": "You are a professional interview assistant..."
        }]
    },
    voice={
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM"
    }
)
```

### Making a Call
```python
# Make a call using the assistant
call = vapi.calls.create(
    assistantId=assistant.id,
    customer={
        "number": "+1234567890"
    }
)
```

## Webhook Events

### Status Updates
```json
{
  "message": {
    "type": "status-update",
    "call": {
      "id": "call_123",
      "status": "in-progress"
    }
  }
}
```

### Transcripts
```json
{
  "message": {
    "type": "transcript",
    "role": "user",
    "transcript": "Hello, I'm ready for the interview",
    "call": {
      "id": "call_123"
    }
  }
}
```

### Function Calls
```json
{
  "message": {
    "type": "function-call",
    "functionCall": {
      "name": "store_interview_response",
      "parameters": {
        "question": "Tell me about yourself",
        "response": "I'm a software engineer with 5 years experience"
      }
    }
  }
}
```

## Integration with Interview Service

The webhook handler can be integrated with your existing interview service:

1. **Store Transcripts**: Save conversation transcripts to your database
2. **Function Calls**: Handle interview-specific functions like storing responses
3. **Call Completion**: Process end-of-call reports and generate analysis

## Testing

### 1. Test Connection
```bash
curl -X GET http://localhost:8000/api/v1/voice/test-connection \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Create Assistant
```bash
curl -X POST http://localhost:8000/api/v1/voice/create-assistant \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "Test Assistant", "first_message": "Hello!"}'
```

### 3. Make Test Call
```bash
curl -X POST http://localhost:8000/api/v1/voice/make-call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"assistant_id": "assistant_id", "phone_number": "+1234567890"}'
```

### 4. Use the Voice Test Page
Navigate to `/voice-test` in your frontend to use the interactive test interface.

### 5. Run Interactive Test Script
```bash
python test_vapi_integration.py
```

## Next Steps

1. **Add VAPI_KEY to your environment**
2. **Run the test script to create assistants**
3. **Test webhook endpoints**
4. **Integrate with your interview flow**
5. **Add function calls for interview-specific actions**

## Troubleshooting

### Common Issues
1. **API Key Not Set**: Make sure VAPI_KEY environment variable is set
2. **Webhook Not Receiving**: Check your webhook URL in VAPI dashboard
3. **Call Failures**: Verify phone number format and assistant configuration

### Debug Commands
```bash
# Check if VAPI key is set
echo $VAPI_KEY

# Test webhook endpoint
curl -X GET http://localhost:8000/api/v1/voice/vapi-webhook/test

# Run test script
python test_vapi_integration.py
```
