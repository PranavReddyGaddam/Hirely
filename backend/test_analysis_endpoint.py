import requests
import json

# Test if the analysis endpoint is accessible
token = input("Enter your hirely_token from localStorage: ").strip()
interview_id = "003689b2-efe7-4d31-8bb1-25437154252a"  # Most recent interview

print(f"\n🧪 Testing /interview-analysis/start endpoint...")
print(f"Interview ID: {interview_id[:8]}...")

response = requests.post(
    "http://localhost:8000/api/v1/interview-analysis/start",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "interview_id": interview_id,
        "conversation_id": None
    }
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    print("\n✅ Analysis endpoint is working!")
else:
    print(f"\n❌ Analysis endpoint failed: {response.status_code}")
