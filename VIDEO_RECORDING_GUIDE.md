# 🎥 Interview Video Recording & Analysis Guide

## ✅ What Was Implemented

### Frontend (InterviewSession.tsx)
1. **Automatic Video Recording**
   - Starts when interview answering phase begins (after prep time)
   - Records entire interview session
   - Stops when interview completes
   - Auto-downloads video to `Downloads` folder

2. **MediaRecorder Integration**
   - Format: WebM (VP9 or VP8 codec)
   - Quality: 2.5 Mbps bitrate
   - Filename: `interview_[ID]_[timestamp].webm`

### Backend (video_analysis.py)
1. **POST /api/v1/video/analyze-saved-interview**
   - Accepts uploaded video file
   - Extracts frames at 5 FPS
   - Runs full CV analysis
   - Generates behavioral metrics
   - Returns AI insights via Groq

2. **GET /api/v1/video/supported-formats**
   - Lists supported video formats
   - Provides codec information

---

## 🚀 How It Works

### Recording Flow:
```
1. User starts interview
   ↓
2. Camera activates
   ↓
3. CV real-time tracking starts
   ↓
4. Prep phase (20s) - NO RECORDING
   ↓
5. Answering begins - VIDEO RECORDING STARTS ✅
   ↓
6. User answers questions (recording continues)
   ↓
7. Interview completes - VIDEO RECORDING STOPS ✅
   ↓
8. Video auto-downloads to Downloads folder
   ↓
9. User can now analyze the saved video
```

---

## 🧪 Testing Instructions

### Step 1: Start the Backend
```bash
cd /Users/pranav/Projects/Calhacks/backend
source venv/bin/activate
python start_server.py
```

### Step 2: Start the Frontend
```bash
cd /Users/pranav/Projects/Calhacks/frontend
npm run dev
```

### Step 3: Conduct a Test Interview
1. Open browser: `http://localhost:5173`
2. Login to your account
3. Start an interview
4. **Allow camera permissions**
5. Wait through prep phase (20 seconds)
6. Start answering (recording begins automatically)
7. Complete the interview
8. **Check your Downloads folder** for the video file

### Step 4: Verify Recording
Look for file named: `interview_[ID]_[timestamp].webm`

Example: `interview_abc123_1730000000000.webm`

**Check the browser console for logs:**
```
[Video Recording] Interview answering started, beginning video recording...
[Video Recording] Started recording with video/webm;codecs=vp9
[Video Recording] Interview ID: abc123
[Video Recording] Chunk recorded: 125000 bytes
[Video Recording] Chunk recorded: 128000 bytes
...
[Video Recording] Interview completed, stopping video recording...
[Video Recording] Recording stopped, saving video...
[Video Recording] Created video blob: 15.23 MB
[Video Recording] ✅ Video saved: interview_abc123_1730000000000.webm
[Video Recording] Video downloaded to your Downloads folder
```

### Step 5: Analyze the Saved Video

#### Option A: Using curl
```bash
# Replace with your actual file path and interview ID
curl -X POST http://localhost:8000/api/v1/video/analyze-saved-interview \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -F "video=@/Users/pranav/Downloads/interview_abc123_1730000000000.webm" \
  -F "interview_id=abc123"
```

#### Option B: Using Python
```python
import requests

# Get auth token
token = "YOUR_AUTH_TOKEN"

# Path to downloaded video
video_path = "/Users/pranav/Downloads/interview_abc123_1730000000000.webm"
interview_id = "abc123"

# Upload and analyze
with open(video_path, 'rb') as f:
    response = requests.post(
        "http://localhost:8000/api/v1/video/analyze-saved-interview",
        headers={"Authorization": f"Bearer {token}"},
        files={"video": f},
        data={"interview_id": interview_id}
    )

# Get results
result = response.json()
print(f"✅ Analysis complete!")
print(f"Frames analyzed: {result['video_info']['frames_analyzed']}")
print(f"Duration: {result['video_info']['duration_seconds']:.1f}s")
print(f"\nExport files created:")
print(f"  - {result['export_files']['interview_analysis']}")
print(f"  - {result['export_files']['session']}")
```

#### Option C: Using Postman
1. Create POST request to: `http://localhost:8000/api/v1/video/analyze-saved-interview`
2. Add Authorization header: `Bearer YOUR_TOKEN`
3. Body → form-data:
   - Key: `video` (type: File) → Select your .webm file
   - Key: `interview_id` (type: Text) → Enter interview ID
4. Send request

### Step 6: Check Analysis Results

The endpoint returns:
```json
{
  "success": true,
  "message": "Video analysis completed successfully",
  "video_info": {
    "filename": "interview_abc123_1730000000000.webm",
    "duration_seconds": 120.5,
    "total_frames": 3614,
    "frames_analyzed": 602,
    "target_fps": 5,
    "actual_fps": 4.99
  },
  "cv_analysis": {
    "session_info": {...},
    "overall_interview_score": {...},
    "emotions": {...},
    "facial_metrics": {...},
    "head_pose": {...},
    "postures": {...},
    "gestures": {...},
    "stress": {...},
    "attention": {...}
  },
  "ai_insights": {
    "overall_assessment": "...",
    "strengths": [...],
    "improvements": [...],
    "recommendations": [...]
  },
  "export_files": {
    "interview_analysis": "exports/interview_analysis_20251025_123456.json",
    "session": "exports/session_20251025_123456.json"
  }
}
```

---

## 📊 What Gets Analyzed

### Real-time During Interview:
- Facial expressions (calm, happy, sad, surprised, tense)
- Eye contact percentage
- Blink rate (stress indicator)
- Head movements (yaw, pitch, roll)
- Posture quality (slouching detection)
- Hand gestures (face touching, fidgeting)
- Attention/engagement levels

### From Saved Video:
- **Same metrics** but processed offline
- More reliable (no network issues)
- Can re-analyze same video multiple times
- Can process at different FPS if needed

---

## 🔧 Configuration

### Video Recording Settings
Located in: `frontend/src/pages/InterviewSession.tsx`

```typescript
const mediaRecorder = new MediaRecorder(mediaStreamRef.current, {
  mimeType: 'video/webm;codecs=vp9',
  videoBitsPerSecond: 2500000 // Adjust quality (default: 2.5 Mbps)
});

mediaRecorder.start(1000); // Capture chunks every 1000ms
```

**Adjust bitrate for different quality/size:**
- 1000000 (1 Mbps) - Lower quality, smaller file
- 2500000 (2.5 Mbps) - **Default**, good balance
- 5000000 (5 Mbps) - Higher quality, larger file

### Video Analysis Settings
Located in: `backend/app/api/v1/endpoints/video_analysis.py`

```python
# Process video at 5 FPS (extract every Nth frame)
target_fps = 5  # Change to 10 for more frames, 3 for less

# JPEG quality for frame encoding
cv2.IMWRITE_JPEG_QUALITY, 85  # 0-100, higher = better quality
```

---

## 🐛 Troubleshooting

### Video Not Recording
**Check browser console for:**
```
[Video Recording] Cannot start - missing media stream or interview ID
```
**Solution:** Ensure camera permissions granted and video is playing

### No Video Download
**Check console for:**
```
[Video Recording] No recorded chunks to save
```
**Solution:** Recording may not have started. Check that answering phase began.

### Video Analysis Fails
**Error:** `Failed to open video file`
**Solution:** 
- Ensure video format is supported (WebM, MP4)
- Check file is not corrupted
- Try converting to MP4: `ffmpeg -i input.webm output.mp4`

### CV Analysis Shows No Face
**Symptom:** All metrics are 0, `face_detected: false`
**Solution:**
- Check lighting in video
- Ensure face is visible and not too far/close
- MediaPipe requires clear face visibility

### Large File Size
**If video is too large (>100MB for 2min):**
- Reduce bitrate in frontend (line 299)
- Use VP8 instead of VP9 (smaller but lower quality)
- Compress video: `ffmpeg -i input.webm -b:v 1M output.webm`

---

## 📁 File Locations

### Frontend Files Modified
```
frontend/src/pages/InterviewSession.tsx
  - Lines 41-44: Video recording state
  - Lines 280-398: Recording functions
  - Lines 165-175: Auto start/stop logic
```

### Backend Files Created
```
backend/app/api/v1/endpoints/video_analysis.py (NEW)
  - POST /video/analyze-saved-interview
  - GET /video/supported-formats
```

### Backend Files Modified
```
backend/app/api/v1/api.py
  - Line 2: Import video_analysis
  - Line 16: Register router
```

---

## 🎯 Use Cases

### 1. Live Interview with Real-time Feedback
- ✅ Real-time CV tracking during interview
- ✅ Real-time overlay metrics
- ✅ Video saved for backup/review

### 2. Post-Interview Analysis
- ✅ Upload recorded video
- ✅ Run comprehensive CV analysis
- ✅ Generate detailed reports
- ✅ Compare multiple takes

### 3. Offline Analysis
- ✅ Record interview without backend
- ✅ Upload later when backend available
- ✅ Batch process multiple videos

### 4. Quality Assurance
- ✅ Review borderline interview performance
- ✅ Re-analyze with different settings
- ✅ Audit CV accuracy

---

## ✅ Testing Checklist

- [ ] Video records during answering phase (not prep)
- [ ] Video downloads automatically after interview
- [ ] File size is reasonable (2-5MB per minute)
- [ ] Video plays correctly in VLC/browser
- [ ] Backend accepts and processes video
- [ ] CV analysis runs successfully
- [ ] Export JSON files created
- [ ] AI insights generated
- [ ] Browser console shows recording logs
- [ ] Backend logs show frame processing

---

## 🎉 Success Indicators

### Frontend Success:
```
✅ [Video Recording] Started recording with video/webm;codecs=vp9
✅ [Video Recording] Chunk recorded: 125000 bytes (repeating)
✅ [Video Recording] Recording stopped, saving video...
✅ [Video Recording] Created video blob: 15.23 MB
✅ [Video Recording] ✅ Video saved: interview_abc123_1730000000000.webm
```

### Backend Success:
```
✅ [Video Analysis] Starting analysis for interview abc123
✅ [Video Analysis] Saved video to temp file: /tmp/tmp_abc.webm
✅ [Video Analysis] Video properties: 30.00 FPS, 3614 frames, 120.47s duration
✅ [Video Analysis] Processing every 6 frames (targeting 5 FPS)
✅ [Video Analysis] Processed 25 frames...
✅ [Video Analysis] Processed 50 frames...
...
✅ [Video Analysis] Finished processing 602 frames from 3614 total frames
✅ [Video Analysis] Analysis complete for interview abc123
```

---

## 📚 Additional Resources

- **OpenCV Documentation**: https://docs.opencv.org/
- **MediaRecorder API**: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
- **WebM Format**: https://www.webmproject.org/
- **CV System Details**: See `/backend/app/cv/` directory

---

## 🔮 Future Enhancements

Potential improvements:
1. Cloud storage upload option
2. Real-time streaming analysis
3. Multiple video quality presets
4. Video editing/trimming before upload
5. Side-by-side comparison tool
6. Export video with overlay annotations
7. Mobile app support
8. Progressive upload during recording

---

**Built with:**
- Frontend: React + TypeScript + MediaRecorder API
- Backend: FastAPI + OpenCV + MediaPipe
- CV Analysis: DeepFace (fallback mode) + MediaPipe
- AI Insights: Groq LLaMA 3.1 70B

