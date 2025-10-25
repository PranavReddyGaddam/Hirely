# 🧪 Testing Guide - Analytics Dashboard

## 🚀 Quick Start

### 1. Start Backend
```bash
cd /Users/pranav/Projects/Calhacks/backend
source venv/bin/activate
python start_server.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend
```bash
cd /Users/pranav/Projects/Calhacks/frontend
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## 📝 Test Scenario 1: Complete Interview Flow

### Step 1: Login
1. Go to `http://localhost:5173/login`
2. Enter your credentials
3. Click "Login"

### Step 2: Start Interview
1. Click "Start Interview" on homepage
2. Fill in interview setup:
   - **Interview Type**: Mixed (or any)
   - **Number of Questions**: 1 (for quick testing)
   - **Job Description**: (Optional)
3. Click "Start Interview"

### Step 3: During Interview
**What to expect:**
- ✅ Camera activates
- ✅ Voice agent starts (ElevenLabs)
- ✅ Video recording starts automatically
- ✅ Voice agent asks questions and responds
- ✅ Questions appear on left side
- ✅ Video feed on right side

**Console Logs to Watch:**
```javascript
[VoiceAgent] Conversation ID: conv_abc123xyz
[InterviewSession] Conversation ID received: conv_abc123xyz
```

### Step 4: Complete Interview
1. Answer all questions
2. Click "Next Question" after each answer
3. When you see "No more questions":
   - ✅ Video stops recording
   - ✅ Video uploads to Supabase
   - ✅ Analysis triggers automatically
   - ✅ Redirects to analytics page

**Console Logs:**
```javascript
[Analysis] Triggering comprehensive analysis...
[Analysis] Interview ID: int_123
[Analysis] Conversation ID: conv_abc123xyz
[Analysis] ✅ Analysis started: { status: "pending", progress: 0 }
```

### Step 5: Watch Loading Screen
**You should see:**
- 🔄 Animated spinner with percentage (0% → 100%)
- 📊 Progress bar filling up
- 📝 Status messages updating:
  - ✅ Video uploaded to secure storage
  - ⏳ Analyzing visual behavior...
  - ⏳ Analyzing communication...
  - ⏳ Generating AI insights...

**Time Estimate:** 45-60 seconds

**What's Happening in Backend:**
```
[Analysis Orchestrator] Starting analysis for interview int_123
[Analysis Orchestrator] Interview found: mixed
[Analysis Orchestrator] Running CV analysis on video: user_id/int_123/video.webm
[CV Analysis] Downloading video from storage
[CV Analysis] Video saved to temp: /tmp/tmpXYZ.webm
[CV Analysis] Processing video: 300 frames at 30 FPS
[CV Analysis] Processed 60 frames
[Analysis Orchestrator] Getting transcript from ElevenLabs: conv_abc123xyz
[Analysis Orchestrator] Analyzing transcript (1523 chars)
[Analysis Orchestrator] Generating AI insights with Groq
[Analysis Orchestrator] ✅ Analysis complete in 52.3s
```

### Step 6: View Analytics Dashboard
**What you'll see:**

#### 1. Overall Score Card (Top)
```
┌─────────────────────────────────────────────┐
│  Overall Performance                        │
│  Combined CV and Communication Analysis     │
│                                             │
│            85                Grade: A       │
│                                             │
│  Visual Behavior: 68/100                   │
│  Communication: 92/100                     │
└─────────────────────────────────────────────┘
```

#### 2. Two-Column Layout

**Left Side: Visual Behavior Analysis** 👁️
```
🎭 Emotional State
  - Dominant Emotion: Calm
  - Emotional Stability: High
  - Expression Distribution:
    ▓▓▓▓▓▓▓▓▓▓░░░░░░ Calm: 100%
    ░░░░░░░░░░░░░░░░ Happy: 0%
    ░░░░░░░░░░░░░░░░ Surprised: 0%

👀 Eye Contact
  - Looking at Camera: 0%
  ░░░░░░░░░░░░░░░░

🧘 Posture
  - Good Posture: 0%
  ░░░░░░░░░░░░░░░░
```

**Right Side: Communication Analysis** 🎤
```
Filler Words
  Total: 15 filler words
  Percentage: 3.2%
  Most used: "um" (8x)
  Rating: Good ✅

⏱️ Speaking Pace
  145 WPM
  Rating: Optimal ✅

📚 Vocabulary
  Unique: 320/500
  Diversity: 64%
  Rating: Excellent ✅

Communication Score: 92/100 (A)
```

#### 3. AI Insights Section
```
🤖 AI-Powered Insights

Your interview performance was strong overall. You demonstrated
excellent vocabulary diversity and maintained an optimal speaking
pace throughout. Your communication score of 92/100 reflects your
ability to articulate thoughts clearly...

💪 Top 3 Strengths:
1. Excellent vocabulary diversity (64% unique words)
2. Optimal speaking pace (145 WPM)
3. Minimal filler words (3.2%)

🎯 Top 3 Areas for Improvement:
1. Eye contact needs significant improvement (0%)
2. Posture could be better (slouching detected)
3. Consider adding more facial expressions

🔧 Detailed Recommendations:
1. Practice looking directly at the camera...
2. Sit upright with shoulders back...
...
```

#### 4. Full Transcript
```
📝 Full Transcript

[Scrollable box with full conversation text]
"Hello, I'm excited to be here today. Um, I have been working
in software development for about five years now. Like, my main
expertise is in React and TypeScript..."

💡 Tip: Filler words are highlighted for your reference
```

#### 5. Action Buttons
```
[Back to Profile]  [📄 Download Report (PDF)]
```

---

## 🧪 Test Scenario 2: Test Individual Components

### Test 1: Transcript Analyzer
```bash
cd /Users/pranav/Projects/Calhacks/backend
python3 << 'EOF'
from app.services.transcript_analyzer import TranscriptAnalyzer

analyzer = TranscriptAnalyzer()
transcript = """
Hello, um, I'm really excited to be here today. Like, I have been working
in software development for about five years now. You know, my main expertise
is in React and TypeScript. Um, I really enjoy building user interfaces.
"""
results = analyzer.analyze_transcript(transcript, duration_seconds=30)

print("Filler Words:", results['filler_word_analysis']['total_filler_words'])
print("Filler %:", results['filler_word_analysis']['filler_percentage'])
print("WPM:", results['speaking_pace']['words_per_minute'])
print("Score:", results['communication_score']['score'])
EOF
```

**Expected Output:**
```
Filler Words: 4
Filler %: 10.26
WPM: 158.0
Score: 68.0
```

### Test 2: ElevenLabs Transcript Retrieval
```bash
cd /Users/pranav/Projects/Calhacks/backend
python3 << 'EOF'
import asyncio
from app.services.elevenlabs_service import ElevenLabsService

async def test():
    service = ElevenLabsService()
    # Use a real conversation ID from your logs
    result = await service.get_conversation_transcript("conv_YOUR_ID_HERE")
    if result:
        print("Transcript:", result['full_transcript'][:100])
        print("Messages:", len(result['messages']))
    else:
        print("Failed to get transcript")

asyncio.run(test())
EOF
```

### Test 3: Analysis API
```bash
# Get auth token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpass"}' | jq -r '.access_token')

# Start analysis
curl -X POST http://localhost:8000/api/v1/interview-analysis/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "interview_id": "YOUR_INTERVIEW_ID",
    "conversation_id": "YOUR_CONVERSATION_ID"
  }' | jq

# Check status (run multiple times)
curl http://localhost:8000/api/v1/interview-analysis/status/YOUR_INTERVIEW_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# Get results (when status is "completed")
curl http://localhost:8000/api/v1/interview-analysis/results/YOUR_INTERVIEW_ID \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 🔍 Debugging

### Check Backend Logs
**Look for these key log messages:**

```
✅ GOOD:
[Analysis Orchestrator] Starting analysis for interview int_123
[Analysis Orchestrator] ✅ Analysis complete in 52.3s
[Analysis API] Start analysis request for interview int_123
[Analysis API] Background analysis complete for int_123

❌ ERRORS:
[Analysis Orchestrator] Error during analysis: [error details]
[CV Analysis] Failed to download video
[Analysis API] Background analysis error: [error details]
```

### Check Frontend Console
**Look for these:**

```javascript
✅ GOOD:
[InterviewSession] Conversation ID received: conv_abc123xyz
[Analysis] Triggering comprehensive analysis...
[Analysis] ✅ Analysis started: { status: "pending" }

❌ ERRORS:
[Analysis] No auth token found
[Analysis] Failed to start analysis: 401
[Analysis] Error triggering analysis: [error]
```

### Common Issues

#### Issue: No conversation ID
**Symptom:** `[Analysis] Conversation ID: none`
**Cause:** VoiceAgent didn't capture ID
**Fix:**
1. Check ElevenLabs API key
2. Check VoiceAgent console logs
3. Verify `onConversationIdReady` callback

#### Issue: Video not found
**Symptom:** `[Analysis Orchestrator] No video found`
**Cause:** Video didn't upload to Supabase
**Fix:**
1. Check Supabase configuration
2. Check video upload logs
3. Verify bucket permissions

#### Issue: Analysis stuck at 10%
**Symptom:** Progress bar doesn't move
**Cause:** CV processing failed
**Fix:**
1. Check backend logs for errors
2. Verify video file is valid
3. Check OpenCV/MediaPipe installation

#### Issue: No transcript
**Symptom:** Communication analysis shows 0 words
**Cause:** Couldn't get ElevenLabs transcript
**Fix:**
1. Check conversation_id is valid
2. Verify ElevenLabs API key
3. Check if conversation exists in ElevenLabs dashboard

---

## ✅ Success Criteria

### You know it's working when:

1. ✅ Interview completes without errors
2. ✅ Video uploads to Supabase (check storage bucket)
3. ✅ Analysis triggers automatically (check console)
4. ✅ Loading screen appears with progress
5. ✅ Progress bar moves from 0% to 100%
6. ✅ Dashboard loads with all sections:
   - Overall score card
   - CV analysis (emotions, eye contact, posture)
   - Transcript analysis (filler words, pace, vocabulary)
   - AI insights
   - Full transcript
7. ✅ All numbers are realistic (not all zeros)
8. ✅ No error messages or red text

### Red Flags:

- ❌ Analysis status stays "pending" forever
- ❌ Progress stuck at 0%
- ❌ All metrics show 0 or N/A
- ❌ Error page appears
- ❌ "Failed to start analysis" message

---

## 📊 Expected Results (Sample Data)

### For a typical 3-minute interview:

**CV Analysis:**
- Emotions: Mostly "calm" (80-100%)
- Eye Contact: Varies (0-60%)
- Posture: Varies (40-80%)
- Overall CV Score: 60-80

**Transcript Analysis:**
- Total Words: 300-500
- Filler Words: 10-30 (2-6%)
- WPM: 120-160
- Vocabulary Diversity: 0.5-0.7
- Communication Score: 70-90

**Overall Score:**
- Combined: 65-85
- Grade: B to A

---

## 🎯 Testing Checklist

Before declaring success, test:

- [ ] Complete 1-question interview
- [ ] Complete 3-question interview
- [ ] Complete 5-question interview
- [ ] Test different interview types (mixed, behavioral, technical)
- [ ] Test with good speaking (minimal fillers)
- [ ] Test with bad speaking (many fillers)
- [ ] Test with different camera angles
- [ ] Test with good posture
- [ ] Test with slouching
- [ ] Test download PDF feature
- [ ] Test back to profile button
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile (responsive design)
- [ ] Test with slow internet
- [ ] Test API error handling (disconnect backend mid-analysis)

---

## 🚀 You're Ready!

Follow the test scenarios above to verify everything works. The analytics dashboard should provide comprehensive insights into interview performance.

**Happy Testing! 🎉**

