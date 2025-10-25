"""
Test OpenRouter LLM Service
Tests the OpenRouter API to verify it works before integrating into analysis orchestrator
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openrouter():
    """Test OpenRouter API with a simple chat completion"""
    
    # Get API key from environment
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment variables")
        print("   Please set it in your .env file:")
        print("   OPENROUTER_API_KEY=your_key_here")
        return False
    
    print("="*80)
    print("🧪 Testing OpenRouter LLM Service")
    print("="*80)
    print()
    
    # Test 1: Simple text generation
    print("📝 Test 1: Simple Text Generation")
    print("-" * 80)
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Hirely Interview Analysis",
            },
            data=json.dumps({
                "model": "anthropic/claude-sonnet-4.5",
                "messages": [
                    {
                        "role": "user",
                        "content": "Write a brief (2-3 sentence) summary of what makes a good job interview."
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.7
            }),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print("✅ Success!")
            print()
            print("Response:")
            print("-" * 80)
            print(content)
            print("-" * 80)
            print()
            
            # Show token usage
            if 'usage' in data:
                usage = data['usage']
                print(f"📊 Token Usage:")
                print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
                print()
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Interview analysis scenario (similar to what we'll use)
    print()
    print("📊 Test 2: Interview Analysis Scenario")
    print("-" * 80)
    
    try:
        analysis_prompt = """You are an expert interview coach providing feedback.

CV Analysis:
- Emotions: Calm (90%), Happy (10%)
- Eye Contact: Looking at camera 85% of the time
- Posture: Good posture 75% of the time
- Overall CV Score: 82/100

Transcript Analysis:
- Filler Words: 12 words (2.8%)
- Speaking Pace: 142 WPM (optimal)
- Vocabulary Diversity: 68% unique words
- Communication Score: 88/100

Provide:
1. A brief executive summary (2-3 sentences)
2. Top 2 strengths
3. Top 2 areas for improvement
4. 3 specific recommendations

Keep it concise and actionable."""

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Hirely Interview Analysis",
            },
            data=json.dumps({
                "model": "anthropic/claude-sonnet-4.5",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert interview coach providing comprehensive, constructive feedback."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print("✅ Success!")
            print()
            print("Analysis Response:")
            print("=" * 80)
            print(content)
            print("=" * 80)
            print()
            
            # Show token usage
            if 'usage' in data:
                usage = data['usage']
                print(f"📊 Token Usage:")
                print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
                print()
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("="*80)
    print("✅ All tests passed! OpenRouter is working correctly.")
    print("="*80)
    print()
    print("💡 Next steps:")
    print("   1. Update interview_analysis_orchestrator.py to use OpenRouter")
    print("   2. Update the generate_ai_insights method")
    print("   3. Replace Groq with OpenRouter (anthropic/claude-sonnet-4.5)")
    print()
    
    return True


if __name__ == "__main__":
    success = test_openrouter()
    exit(0 if success else 1)
