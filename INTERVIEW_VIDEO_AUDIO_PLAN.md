# Interview Video/Audio Interface Plan - Hackathon Day

## Overview
This document outlines the implementation of video and audio functionality for the interview screen, including camera access, video display, audio recording, and real-time feedback features.

## Current Status
- **Interview Session Page**: Basic structure exists (`frontend/src/pages/InterviewSession.tsx`)
- **Question Display**: Working with timer and navigation
- **Audio Recording**: Not yet implemented
- **Video Display**: Not yet implemented
- **Camera Access**: Not yet implemented

## Hackathon Day Tasks

### 1. Camera Access and Video Display

#### 1.1 Camera Permission and Access
**Priority: HIGH**
- **Task**: Implement camera access with user permission
- **Location**: `frontend/src/pages/InterviewSession.tsx`
- **Implementation**:
  ```typescript
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: true
      });
      setCameraStream(stream);
    } catch (error) {
      setCameraError('Camera access denied or unavailable');
    }
  };
  ```

#### 1.2 Video Display Component
**Priority: HIGH**
- **Task**: Create video preview component for self-view
- **Location**: `frontend/src/pages/InterviewSession.tsx`
- **Features**:
  - Real-time video preview
  - Picture-in-picture mode
  - Video quality controls
  - Recording indicator

#### 1.3 Video Controls
**Priority: MEDIUM**
- **Task**: Add video control buttons (start/stop camera, mute/unmute)
- **Implementation**:
  ```typescript
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  
  const toggleVideo = () => {
    if (cameraStream) {
      const videoTrack = cameraStream.getVideoTracks()[0];
      videoTrack.enabled = !videoTrack.enabled;
      setIsVideoEnabled(videoTrack.enabled);
    }
  };
  
  const toggleAudio = () => {
    if (cameraStream) {
      const audioTrack = cameraStream.getAudioTracks()[0];
      audioTrack.enabled = !audioTrack.enabled;
      setIsAudioEnabled(audioTrack.enabled);
    }
  };
  ```

### 2. Audio Recording and Processing

#### 2.1 Audio Recording Implementation
**Priority: HIGH**
- **Task**: Implement audio recording during interview responses
- **Location**: `frontend/src/pages/InterviewSession.tsx`
- **Implementation**:
  ```typescript
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  
  const startRecording = () => {
    if (cameraStream) {
      const recorder = new MediaRecorder(cameraStream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      const chunks: BlobPart[] = [];
      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };
      
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
      };
      
      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };
  ```

#### 2.2 Audio Duration Tracking
**Priority: MEDIUM**
- **Task**: Track audio recording duration
- **Implementation**:
  ```typescript
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordingTimer, setRecordingTimer] = useState<NodeJS.Timeout | null>(null);
  
  const startRecordingTimer = () => {
    setRecordingDuration(0);
    const timer = setInterval(() => {
      setRecordingDuration(prev => prev + 1);
    }, 1000);
    setRecordingTimer(timer);
  };
  
  const stopRecordingTimer = () => {
    if (recordingTimer) {
      clearInterval(recordingTimer);
      setRecordingTimer(null);
    }
  };
  ```

### 3. UI/UX Implementation

#### 3.1 Split-Screen Layout
**Priority: HIGH**
- **Task**: Implement split-screen layout for video and questions
- **Location**: `frontend/src/pages/InterviewSession.tsx`
- **Layout**:
  ```
  ┌─────────────────┬─────────────────┐
  │   Video Feed    │   Question      │
  │   (Self View)   │   & Controls    │
  │                 │                 │
  │   [Recording]   │   [Timer]       │
  │   [Controls]    │   [Navigation]  │
  └─────────────────┴─────────────────┘
  ```

#### 3.2 Video Component Styling
**Priority: MEDIUM**
- **Task**: Style video component with glassmorphic design
- **Implementation**:
  ```typescript
  const VideoPreview = () => (
    <div className="relative bg-white/20 backdrop-blur-md border border-white/30 rounded-2xl shadow-xl overflow-hidden">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="w-full h-full object-cover"
      />
      {isRecording && (
        <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
          ● REC
        </div>
      )}
      <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center">
        <button
          onClick={toggleVideo}
          className={`p-2 rounded-full ${isVideoEnabled ? 'bg-lime-500' : 'bg-gray-500'}`}
        >
          {isVideoEnabled ? <VideoIcon /> : <VideoOffIcon />}
        </button>
        <button
          onClick={toggleAudio}
          className={`p-2 rounded-full ${isAudioEnabled ? 'bg-lime-500' : 'bg-gray-500'}`}
        >
          {isAudioEnabled ? <MicIcon /> : <MicOffIcon />}
        </button>
      </div>
    </div>
  );
  ```

### 4. Audio Processing and Analysis

#### 4.1 Audio Transcription
**Priority: MEDIUM**
- **Task**: Implement speech-to-text for interview responses
- **Implementation Options**:
  - Web Speech API (browser-based)
  - Google Cloud Speech-to-Text
  - Azure Speech Services
  - OpenAI Whisper API

#### 4.2 Audio Quality Analysis
**Priority: LOW**
- **Task**: Analyze audio quality (volume, clarity, background noise)
- **Implementation**:
  ```typescript
  const analyzeAudioQuality = (audioBlob: Blob) => {
    // Analyze audio characteristics
    // Return quality metrics
    return {
      volume: 0.8,
      clarity: 0.9,
      backgroundNoise: 0.1,
      overallQuality: 0.85
    };
  };
  ```

### 5. Integration with Backend

#### 5.1 Audio Upload to Backend
**Priority: HIGH**
- **Task**: Send recorded audio to backend for processing
- **Location**: `frontend/src/pages/InterviewSession.tsx`
- **Implementation**:
  ```typescript
  const submitAudioResponse = async (audioBlob: Blob, questionId: string) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'response.webm');
    formData.append('question_id', questionId);
    formData.append('duration', recordingDuration.toString());
    
    const response = await fetch(`/api/v1/interviews/${interviewId}/submit_audio`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    return response.json();
  };
  ```

#### 5.2 Backend Audio Processing
**Priority: MEDIUM**
- **Task**: Create backend endpoint for audio processing
- **Location**: `backend/app/api/v1/endpoints/interviews.py`
- **Implementation**:
  ```python
  @router.post("/{interview_id}/submit_audio")
  async def submit_audio_response(
      interview_id: str,
      audio_file: UploadFile = File(...),
      question_id: str = Form(...),
      duration: int = Form(...),
      current_user = Depends(get_current_user)
  ):
      # Process audio file
      # Transcribe speech
      # Store in database
      # Return transcription and analysis
  ```

### 6. Real-time Features

#### 6.1 Live Transcription Display
**Priority: MEDIUM**
- **Task**: Show live transcription during recording
- **Implementation**:
  ```typescript
  const [liveTranscription, setLiveTranscription] = useState('');
  
  const startLiveTranscription = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            setLiveTranscription(prev => prev + event.results[i][0].transcript);
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        setLiveTranscription(prev => prev + interimTranscript);
      };
      
      recognition.start();
    }
  };
  ```

#### 6.2 Real-time Feedback
**Priority: LOW**
- **Task**: Provide real-time feedback during recording
- **Features**:
  - Speaking pace indicator
  - Volume level indicator
  - Background noise detection
  - Confidence score display

### 7. Error Handling and Fallbacks

#### 7.1 Camera/Audio Error Handling
**Priority: HIGH**
- **Task**: Handle camera and audio access errors gracefully
- **Implementation**:
  ```typescript
  const [mediaError, setMediaError] = useState<string | null>(null);
  
  const handleMediaError = (error: Error) => {
    switch (error.name) {
      case 'NotAllowedError':
        setMediaError('Camera/microphone access denied. Please allow access and refresh.');
        break;
      case 'NotFoundError':
        setMediaError('No camera/microphone found. Please connect a device.');
        break;
      case 'NotReadableError':
        setMediaError('Camera/microphone is being used by another application.');
        break;
      default:
        setMediaError('Unable to access camera/microphone. Please check your device.');
    }
  };
  ```

#### 7.2 Fallback Options
**Priority: MEDIUM**
- **Task**: Provide fallback options when media access fails
- **Options**:
  - Text-only interview mode
  - Audio-only recording
  - Upload pre-recorded audio
  - Use system audio input

### 8. Performance Optimization

#### 8.1 Video Quality Optimization
**Priority: MEDIUM**
- **Task**: Optimize video quality based on network conditions
- **Implementation**:
  ```typescript
  const getOptimalVideoConstraints = () => {
    const connection = (navigator as any).connection;
    if (connection) {
      if (connection.effectiveType === '4g') {
        return { width: 1280, height: 720 };
      } else if (connection.effectiveType === '3g') {
        return { width: 640, height: 480 };
      } else {
        return { width: 320, height: 240 };
      }
    }
    return { width: 640, height: 480 };
  };
  ```

#### 8.2 Memory Management
**Priority: MEDIUM**
- **Task**: Manage memory usage for video/audio recording
- **Implementation**:
  ```typescript
  const cleanupMediaStream = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
  };
  
  useEffect(() => {
    return () => {
      cleanupMediaStream();
    };
  }, []);
  ```

## Implementation Priority Order

### Day 1 (Morning)
1. **Camera Access** - Basic camera permission and video display
2. **Video Component** - Self-view video component with controls
3. **Split-Screen Layout** - Update interview session layout

### Day 1 (Afternoon)
4. **Audio Recording** - Basic audio recording functionality
5. **Audio Upload** - Send audio to backend
6. **Error Handling** - Handle media access errors

### Day 2 (If Time Permits)
7. **Live Transcription** - Real-time speech-to-text
8. **Audio Analysis** - Quality analysis and feedback
9. **Performance Optimization** - Video quality and memory management

## Technical Requirements

### Browser Compatibility
- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Limited support (iOS restrictions)
- **Edge**: Full support

### Required Permissions
- Camera access
- Microphone access
- Media device enumeration

### Dependencies
```json
{
  "dependencies": {
    "lucide-react": "^0.263.1" // For icons
  }
}
```

## UI/UX Considerations

### Design Principles
- **Glassmorphic Design**: Match existing profile page styling
- **Lime/Sky Blue Colors**: Use brand colors for controls
- **Responsive Layout**: Work on desktop and tablet
- **Accessibility**: Screen reader support, keyboard navigation

### User Experience
- **Clear Visual Feedback**: Recording indicators, status messages
- **Intuitive Controls**: Easy-to-understand buttons and icons
- **Error Messages**: Helpful error messages with solutions
- **Performance**: Smooth video playback, minimal lag

## Testing Strategy

### Manual Testing
- Test camera access on different devices
- Test audio recording quality
- Test error handling scenarios
- Test responsive design

### Automated Testing
- Unit tests for media handling functions
- Integration tests for audio upload
- E2E tests for complete interview flow

## Success Metrics

### Technical Metrics
- Camera access success rate: >95%
- Audio recording success rate: >98%
- Video quality: 720p minimum
- Audio quality: Clear speech recognition

### User Experience Metrics
- Interview completion rate
- User satisfaction with video interface
- Error recovery success rate
- Performance on different devices

## Troubleshooting Guide

### Common Issues
1. **Camera Not Working**: Check permissions, device availability
2. **Audio Not Recording**: Check microphone permissions, device selection
3. **Poor Video Quality**: Adjust constraints, check network
4. **Browser Compatibility**: Use supported browsers, check feature support

### Debug Commands
```javascript
// Check media devices
navigator.mediaDevices.enumerateDevices().then(devices => console.log(devices));

// Check permissions
navigator.permissions.query({name: 'camera'}).then(result => console.log(result));
navigator.permissions.query({name: 'microphone'}).then(result => console.log(result));
```

## Resources

### Documentation
- [MediaDevices API](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

### Code References
- `frontend/src/pages/InterviewSession.tsx` - Main interview page
- `frontend/src/components/` - Reusable components
- `backend/app/api/v1/endpoints/interviews.py` - Backend endpoints

## Notes for Hackathon Day

### Quick Start Checklist
- [ ] Test camera access on development machine
- [ ] Verify microphone permissions
- [ ] Check browser compatibility
- [ ] Test audio recording functionality
- [ ] Verify backend audio upload endpoint

### Emergency Fallbacks
- If camera fails, provide audio-only mode
- If audio fails, provide text input mode
- If both fail, provide file upload option
- If browser doesn't support, show compatibility message

### Demo Preparation
- Prepare test devices with camera/microphone
- Test on different browsers
- Prepare demo scenarios for different error cases
- Test audio quality and transcription accuracy

---

**Last Updated**: October 23, 2024
**Status**: Ready for Hackathon Implementation
**Next Review**: Hackathon Day Morning
