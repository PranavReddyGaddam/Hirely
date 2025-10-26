import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth';
import { SmoothPageTransition, SkeletonCard, SkeletonText, LoadingSpinner } from '../components/SkeletonLoader';
import SystemDesignCanvas from '../components/SystemDesignCanvas';
import SystemDesignChat from '../components/SystemDesignChat';
import VoiceAgent from '../components/VoiceAgent';
import { voiceAgentService, type InterviewVoiceAgent } from '../services/voiceAgentService';

export default function InterviewSession() {
  const { interviewId } = useParams<{ interviewId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [interviewStatus, setInterviewStatus] = useState<'loading' | 'preparing' | 'answering' | 'completed' | 'error'>('loading');
  const [prepTimeLeft, setPrepTimeLeft] = useState(20);
  const [answerTimeLeft, setAnswerTimeLeft] = useState(90);
  const [error, setError] = useState<string | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [interviewType, setInterviewType] = useState<string>('mixed');
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [interviewData, setInterviewData] = useState<any>(null);
  
  // Voice Agent state
  const [voiceAgent, setVoiceAgent] = useState<InterviewVoiceAgent | null>(null);
  const [isVoiceAgentActive, setIsVoiceAgentActive] = useState(false);
  const [voiceAgentError, setVoiceAgentError] = useState<string | null>(null);
  const [hasPlayedIntro, setHasPlayedIntro] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Video Recording state
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
      return;
    }

    if (isAuthenticated && interviewId) {
      startInterviewSession();
    }

    return () => {
      // Stop video recording if active
      if (isRecording && mediaRecorderRef.current?.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      // Cleanup media stream on component unmount
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isAuthenticated, authLoading, interviewId, navigate]);

  // Auto-create voice agent when interview starts
  useEffect(() => {
    if (interviewStatus === 'preparing' && !voiceAgent && !hasPlayedIntro && interviewId && interviewData) {
      console.log('Auto-creating voice agent for full interview...');
      createVoiceAgentForInterview();
    }
  }, [interviewStatus, voiceAgent, hasPlayedIntro, interviewId, interviewData]);

  // Additional useEffect to handle video element setup
  useEffect(() => {
    if (videoRef.current && mediaStreamRef.current && !cameraActive) {
      console.log('Video element ready, setting up stream...');
      videoRef.current.srcObject = mediaStreamRef.current;
      videoRef.current.play().then(() => {
        console.log('Video playing after setup');
        setCameraActive(true);
      }).catch((err) => {
        console.error('Error playing video after setup:', err);
      });
    }
  }, [cameraActive]);

  // Ensure camera stream persists throughout the interview
  const ensureCameraActive = () => {
    if (mediaStreamRef.current && videoRef.current && !cameraActive) {
      console.log('Re-establishing camera connection...');
      videoRef.current.srcObject = mediaStreamRef.current;
      videoRef.current.play().then(() => {
        console.log('Camera re-established');
        setCameraActive(true);
      }).catch((err) => {
        console.error('Error re-establishing camera:', err);
      });
    }
  };

  // Check camera status periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (mediaStreamRef.current && !cameraActive) {
        ensureCameraActive();
      }
    }, 1000); // Check every second

    return () => clearInterval(interval);
  }, [cameraActive]);

  useEffect(() => {
    let prepTimer: number;
    let answerTimer: number;

    // Skip timers for system design mode
    if (interviewType === 'system_design') {
      return;
    }

    if (interviewStatus === 'preparing') {
      prepTimer = setInterval(() => {
        setPrepTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(prepTimer);
            setInterviewStatus('answering');
            setAnswerTimeLeft(90); // Reset answer timer for new question
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else if (interviewStatus === 'answering') {
      answerTimer = setInterval(() => {
        setAnswerTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(answerTimer);
            handleAnswerComplete(); // Automatically complete answer if time runs out
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      clearInterval(prepTimer);
      clearInterval(answerTimer);
    };
  }, [interviewStatus, currentQuestion, interviewType]);

  // Auto-start/stop video recording based on interview status
  useEffect(() => {
    if (interviewStatus === 'answering' && !isRecording && cameraActive) {
      // Start recording when first question answering begins
      console.log('[Video Recording] Interview answering started, beginning video recording...');
      startVideoRecording();
    } else if (interviewStatus === 'completed' && isRecording) {
      // Stop recording when interview completes
      console.log('[Video Recording] Interview completed, stopping video recording...');
      stopVideoRecording();
      
      // Also stop voice agent when interview completes
      if (isVoiceAgentActive) {
        console.log('[Voice Agent] Interview completed, stopping voice agent...');
        stopVoiceAgent();
      }
    }
  }, [interviewStatus, isRecording, cameraActive, isVoiceAgentActive]);

  const fetchInterviewDetails = async () => {
    try {
      const token = localStorage.getItem('hirely_token');
      console.log('Fetching interview details for ID:', interviewId);
      console.log('Using token:', token ? `${token.substring(0, 20)}...` : 'No token');
      
      if (!token) {
        console.error('No authentication token found');
        setError('Authentication required. Please log in again.');
        navigate('/login');
        return 'mixed';
      }

      const response = await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('Interview fetch response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('Interview details fetched:', data);
        console.log('Interview type:', data.interview_type);
        setInterviewType(data.interview_type);
        setInterviewData(data); // Store full interview data
        return data.interview_type;
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Failed to fetch interview details:', response.status, response.statusText, errorData);
        
        if (response.status === 401) {
          console.error('Authentication failed - redirecting to login');
          setError('Session expired. Please log in again.');
          navigate('/login');
          return 'mixed';
        }
        
        if (response.status === 404) {
          console.error('Interview not found - may not have been created properly');
          setError('Interview not found. Please create a new interview.');
          navigate('/interview/setup');
          return 'mixed';
        }
        
        // Try to get interview type from localStorage as fallback
        const savedInterviewType = localStorage.getItem(`interview_${interviewId}_type`);
        if (savedInterviewType) {
          console.log('Using saved interview type:', savedInterviewType);
          setInterviewType(savedInterviewType);
          return savedInterviewType;
        }
        return 'mixed'; // Default fallback
      }
    } catch (err) {
      console.error('Error fetching interview details:', err);
      setError('Network error. Please check your connection and try again.');
      // Try to get interview type from localStorage as fallback
      const savedInterviewType = localStorage.getItem(`interview_${interviewId}_type`);
      if (savedInterviewType) {
        console.log('Using saved interview type from localStorage:', savedInterviewType);
        setInterviewType(savedInterviewType);
        return savedInterviewType;
      }
      return 'mixed'; // Default fallback
    }
  };

  // CV analysis will be done post-interview on the saved video
  // No real-time CV tracking during interview

  /**
   * Start recording the interview video to local storage
   * Records ONLY video (no audio) to prevent echo/resonance
   */
  const startVideoRecording = () => {
    if (!mediaStreamRef.current || !interviewId) {
      console.warn('[Video Recording] Cannot start - missing media stream or interview ID');
      return;
    }

    try {
      // Create a NEW stream with ONLY video tracks (no audio to prevent echo)
      const videoTracks = mediaStreamRef.current.getVideoTracks();
      const videoOnlyStream = new MediaStream();
      
      videoTracks.forEach(track => {
        videoOnlyStream.addTrack(track);
      });

      console.log('[Video Recording] Created video-only stream (no audio to prevent echo)');

      // Check browser support
      if (!MediaRecorder.isTypeSupported('video/webm;codecs=vp9')) {
        console.warn('[Video Recording] VP9 not supported, falling back to VP8');
      }

      // Create MediaRecorder with video-only stream
      const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
        ? 'video/webm;codecs=vp9'
        : 'video/webm;codecs=vp8';

      const mediaRecorder = new MediaRecorder(videoOnlyStream, {
        mimeType,
        videoBitsPerSecond: 2500000 // 2.5 Mbps for good quality
      });

      // Reset chunks array
      recordedChunksRef.current = [];

      // Handle data available event
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
          console.log(`[Video Recording] Chunk recorded: ${event.data.size} bytes`);
        }
      };

      // Handle recording stop event
      mediaRecorder.onstop = () => {
        console.log('[Video Recording] Recording stopped, saving video...');
        saveRecordedVideo();
      };

      // Handle errors
      mediaRecorder.onerror = (event: any) => {
        console.error('[Video Recording] Recording error:', event.error);
      };

      // Start recording (capture data every 1 second)
      mediaRecorder.start(1000);
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);

      console.log(`[Video Recording] Started recording with ${mimeType}`);
      console.log(`[Video Recording] Interview ID: ${interviewId}`);
    } catch (error) {
      console.error('[Video Recording] Error starting recording:', error);
    }
  };

  /**
   * Stop recording and trigger download
   */
  const stopVideoRecording = () => {
    if (!isRecording || !mediaRecorderRef.current) {
      console.warn('[Video Recording] No active recording to stop');
      return;
    }

    try {
      if (mediaRecorderRef.current.state === 'recording') {
        console.log('[Video Recording] Stopping recording...');
        mediaRecorderRef.current.stop();
        setIsRecording(false);
      }
    } catch (error) {
      console.error('[Video Recording] Error stopping recording:', error);
    }
  };

  /**
   * Upload recorded video to Supabase Storage (silently, no download)
   */
  const saveRecordedVideo = async () => {
    if (recordedChunksRef.current.length === 0) {
      console.warn('[Video Recording] No recorded chunks to save');
      return;
    }

    try {
      // Create blob from recorded chunks
      const videoBlob = new Blob(recordedChunksRef.current, {
        type: 'video/webm'
      });

      console.log(`[Video Recording] Created video blob: ${(videoBlob.size / 1024 / 1024).toFixed(2)} MB`);
      console.log('[Video Recording] Uploading to Supabase Storage...');

      // Import video upload service
      const { videoUploadService } = await import('../services/VideoUploadService');

      // Upload to Supabase Storage (no download, silent upload)
      const uploadResult = await videoUploadService.uploadInterviewVideo(
        interviewId!,
        videoBlob,
        (progress) => {
          console.log(`[Video Upload] ${progress.percentage}% (${(progress.loaded / 1024 / 1024).toFixed(2)} MB / ${(progress.total / 1024 / 1024).toFixed(2)} MB)`);
        }
      );

      console.log('[Video Recording] ✅ Video uploaded successfully to Supabase Storage');
      console.log('[Video Recording] Storage path:', uploadResult.storage_path);
      console.log('[Video Recording] Video URL:', uploadResult.video_url);
      console.log('[Video Recording] Size:', uploadResult.size_mb, 'MB');
      
      // Clear recorded chunks
      recordedChunksRef.current = [];
      
      // Store upload result for later use (e.g., CV analysis)
      localStorage.setItem(`interview_${interviewId}_video_url`, uploadResult.video_url);
      localStorage.setItem(`interview_${interviewId}_storage_path`, uploadResult.storage_path);
      
    } catch (error) {
      console.error('[Video Recording] Error uploading video:', error);
      // Don't throw - we don't want to break the interview flow if upload fails
      // The user can always re-upload later
    }
  };

  const startInterviewSession = async () => {
    setInterviewStatus('loading');
    setError(null);
    try {
      // First, fetch interview details to determine type
      const type = await fetchInterviewDetails();
      console.log('Interview type fetched:', type);
      
      // Only request camera access for non-system-design interviews
      if (type !== 'system_design') {
        console.log('Requesting camera access for interview type:', type);
        
        try {
          // Check if getUserMedia is available
          if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error('getUserMedia is not supported in this browser');
          }
          
          // Request camera access with echo cancellation
          console.log('Calling getUserMedia...');
          const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
              width: { ideal: 1280 },
              height: { ideal: 720 },
              facingMode: 'user'
            }, 
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true
            }
          });
          
          console.log('Camera stream obtained successfully:', stream);
          console.log('Video tracks:', stream.getVideoTracks());
          console.log('Audio tracks:', stream.getAudioTracks());
          
          // Store the stream first
          mediaStreamRef.current = stream;
          console.log('Stream stored in ref');
          
          // Set status to preparing immediately after getting the stream
          // The camera will be activated asynchronously
          setInterviewStatus('preparing');
          console.log('Status set to preparing');
          
          // Wait for video element to be ready, then assign stream
          const assignStreamToVideo = () => {
            if (videoRef.current) {
              console.log('Video ref is ready, assigning stream...');
              videoRef.current.srcObject = stream;
              
              // Wait for video to load
              videoRef.current.onloadedmetadata = () => {
                console.log('Video metadata loaded');
                videoRef.current?.play().then(() => {
                  console.log('Video started playing successfully');
                  setCameraActive(true);
                  // Video recording will auto-start when answering begins (via useEffect)
                }).catch((playErr) => {
                  console.error('Error playing video:', playErr);
                  // Don't set error here, camera preview is not critical
                  console.warn('Camera preview failed but interview can continue');
                });
              };
              
              console.log('Camera stream assigned to video element');
            } else {
              console.log('Video ref not ready yet, retrying in 100ms...');
              setTimeout(assignStreamToVideo, 100);
            }
          };
          
          // Start the assignment process
          assignStreamToVideo();
          
        } catch (cameraError) {
          console.error('Camera access failed:', cameraError);
          const errorMessage = cameraError instanceof Error ? cameraError.message : 'Unknown camera error';
          console.warn(`Camera failed but continuing with interview: ${errorMessage}`);
          // Don't block the interview if camera fails
          setInterviewStatus('preparing');
        }
      } else {
        console.log('System design interview - skipping camera setup');
        setInterviewStatus('preparing'); // For system design, directly go to preparing
      }

      // Fetch the first question - but wait for voice intro to complete
      // fetchNextQuestion will be called after voice intro finishes
      console.log('Interview session initialization complete');

    } catch (err) {
      console.error('Error starting interview session:', err);
      if (interviewType === 'system_design') {
        setError('Failed to fetch interview data. Please try again.');
      } else {
        setError('Failed to access camera/microphone or fetch interview data. Please ensure permissions are granted.');
      }
      setInterviewStatus('error');
    }
  };

  const fetchNextQuestion = async () => {
    // Don't set loading status to avoid camera reinitialization
    setError(null);
    try {
      const token = localStorage.getItem('hirely_token');
      console.log('Fetching next question for interview:', interviewId);
      
      if (!token) {
        console.error('No authentication token found for next question');
        setError('Authentication required. Please log in again.');
        navigate('/login');
        return;
      }

      const response = await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}/next_question`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      console.log('Next question fetch response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('Next question fetched:', data);
        if (data.question) {
          setCurrentQuestion(data.question);
          setQuestionIndex(data.question_index);
          setTotalQuestions(data.total_questions);
          setPrepTimeLeft(20); // Reset prep timer
          // Skip preparation phase for system design
          setInterviewStatus(interviewType === 'system_design' ? 'answering' : 'preparing');
        } else {
          // No more questions, interview completed
          setInterviewStatus('completed');
          
          // Stop recording (upload will happen automatically)
          stopVideoRecording();
          
          // Trigger comprehensive analysis (backend will wait for video URL)
          await triggerInterviewAnalysis();
          
          // Redirect to report page (analysis will run in background)
          navigate(`/interview/${interviewId}/report`); // Redirect to report page
        }
      } else if (response.status === 404) {
        // No more questions available - interview completed
        setInterviewStatus('completed');
        
        // Stop recording (upload will happen automatically)
        stopVideoRecording();
        
        // Trigger comprehensive analysis (backend will wait for video URL)
        await triggerInterviewAnalysis();
        
        // Redirect to report page
        navigate(`/interview/${interviewId}/report`); // Redirect to report page
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Failed to fetch next question:', response.status, response.statusText, errorData);
        
        if (response.status === 401) {
          console.error('Authentication failed for next question - redirecting to login');
          setError('Session expired. Please log in again.');
          navigate('/login');
          return;
        }
        
        setError(errorData.detail || 'Failed to fetch next question.');
        setInterviewStatus('error');
      }
    } catch (err) {
      console.error('Error fetching next question:', err);
      setError('Network error or failed to fetch next question.');
      setInterviewStatus('error');
    }
  };

  const handleAnswerComplete = async (earlyCompletion: boolean = false) => {
    // Don't set loading status to preserve camera
    setError(null);
    try {
      const token = localStorage.getItem('hirely_token');
      const response = await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}/submit_answer`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion.id,
          response_text: "Mock answer text (voice input will go here)", // Placeholder
          audio_duration: 90 - answerTimeLeft, // Placeholder
          early_completion: earlyCompletion,
        }),
      });

      if (response.ok) {
        await fetchNextQuestion(); // Move to the next question
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to submit answer.');
        setInterviewStatus('error');
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
      setError('Network error or failed to submit answer.');
      setInterviewStatus('error');
    }
  };

  // System Design Canvas handlers
  const handleScreenshot = async (imageData: string) => {
    try {
      const token = localStorage.getItem('hirely_token');
      await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}/screenshot`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion?.id,
          image_data: imageData,
          timestamp: Date.now(),
        }),
      });
    } catch (err) {
      console.error('Error saving screenshot:', err);
    }
  };

  const handleProgressUpdate = async (progress: any) => {
    try {
      const token = localStorage.getItem('hirely_token');
      await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}/progress`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion?.id,
          progress_data: progress,
        }),
      });
    } catch (err) {
      console.error('Error saving progress:', err);
    }
  };

  const handleChatMessage = async (message: string) => {
    const newMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      message,
      timestamp: new Date(),
    };
    setChatMessages(prev => [...prev, newMessage]);
    setIsTyping(true);

    try {
      const token = localStorage.getItem('hirely_token');
      const response = await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion?.id,
          message,
          context: 'system_design',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai' as const,
          message: data.response,
          timestamp: new Date(),
        };
        setChatMessages(prev => [...prev, aiMessage]);
      }
    } catch (err) {
      console.error('Error sending chat message:', err);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // Voice Agent functions
  const createVoiceAgentForInterview = async () => {
    console.log('Creating voice agent for full interview...', { interviewId, interviewType, interviewData });
    
    if (!interviewId || !interviewData) {
      console.error('No interview ID or data available');
      return;
    }
    
    setVoiceAgentError(null);
    
    try {
      console.log('Calling voiceAgentService.createInterviewAgent...');
      const agent = await voiceAgentService.createInterviewAgent({
        interviewId,
        questionId: currentQuestion?.id,
        interviewType,
        role: 'interviewer',
        enhancedNoiseReduction: true,
        candidateData: interviewData // Pass real interview data
      });
      
      console.log('Voice agent created successfully:', agent);
      setVoiceAgent(agent);
      
      // Auto-start the voice agent and keep it active throughout
      setTimeout(() => {
        if (agent) {
          console.log('Auto-starting voice agent for entire interview...');
          setIsVoiceAgentActive(true);
          setHasPlayedIntro(true); // Mark intro as played
          
          // Load first question after a brief delay
          setTimeout(() => {
            fetchNextQuestion().catch(error => {
              console.error('Error loading first question:', error);
              setError('Failed to load first question');
            });
          }, 2000); // 2 second delay after intro starts
        }
      }, 1000); // Small delay to ensure agent is ready
      
    } catch (error) {
      console.error('Error creating voice agent:', error);
      setVoiceAgentError(error instanceof Error ? error.message : 'Failed to create voice agent');
      
      // If voice agent fails, still load the first question
      setHasPlayedIntro(true);
      fetchNextQuestion().catch(err => {
        console.error('Error loading first question after agent failure:', err);
        setError('Failed to load first question');
      });
    }
  };


  const stopVoiceAgent = async () => {
    console.log('Stopping voice agent (interview complete)...');
    setIsVoiceAgentActive(false);
  };

  const handleVoiceAgentError = async (error: string) => {
    setVoiceAgentError(error);
    setIsVoiceAgentActive(false);
    setHasPlayedIntro(true);
    
    // If voice agent fails, still load the first question
    console.log('Voice agent failed, loading first question anyway...');
    try {
      await fetchNextQuestion();
    } catch (fetchError) {
      console.error('Error loading first question after voice agent failure:', fetchError);
      setError('Failed to load first question');
    }
  };

  const handleConversationIdReady = (convId: string) => {
    console.log('[InterviewSession] Conversation ID received:', convId);
    setConversationId(convId);
    // Store in localStorage as backup
    if (interviewId) {
      localStorage.setItem(`interview_${interviewId}_conversation_id`, convId);
    }
  };

  const triggerInterviewAnalysis = async () => {
    if (!interviewId) return;
    
    try {
      const token = localStorage.getItem('hirely_token');
      if (!token) {
        console.error('[Analysis] No auth token found');
        return;
      }

      // Get conversation ID from state or localStorage
      const convId = conversationId || localStorage.getItem(`interview_${interviewId}_conversation_id`);
      
      console.log('[Analysis] Triggering comprehensive analysis...');
      console.log('[Analysis] Interview ID:', interviewId);
      console.log('[Analysis] Conversation ID:', convId || 'none');

      const response = await fetch('http://localhost:8000/api/v1/interview-analysis/start', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          interview_id: interviewId,
          conversation_id: convId
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('[Analysis] ✅ Analysis started:', result);
      } else {
        console.error('[Analysis] Failed to start analysis:', response.status);
      }
    } catch (err) {
      console.error('[Analysis] Error triggering analysis:', err);
      // Don't block navigation if analysis fails to start
    }
  };

  if (authLoading || interviewStatus === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Header Skeleton */}
          <div className="text-center mb-12">
            <div className="animate-pulse">
              <div className="h-8 bg-slate-200 rounded w-64 mx-auto mb-4"></div>
              <div className="h-4 bg-slate-200 rounded w-96 mx-auto"></div>
            </div>
          </div>

          {/* Interview Setup Skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <SkeletonCard />
            <SkeletonCard />
          </div>

          {/* Question Skeleton */}
          <div className="bg-white rounded-xl p-8 border border-slate-200 shadow-sm mb-8">
            <div className="animate-pulse">
              <div className="h-6 bg-slate-200 rounded w-1/3 mb-6"></div>
              <SkeletonText lines={4} />
            </div>
          </div>

          {/* Loading Animation */}
          <div className="text-center">
            <div className="inline-flex items-center space-x-2 text-slate-600">
              <LoadingSpinner />
              <span>Preparing your interview session...</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (interviewStatus === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-100 text-red-800">
        <div className="text-center">
          <p className="text-lg font-semibold">Error: {error}</p>
          <button 
            onClick={() => navigate('/interview/setup')}
            className="mt-4 px-4 py-2 bg-lime-500 text-white rounded-lg hover:bg-lime-600"
          >
            Back to Setup
          </button>
        </div>
      </div>
    );
  }

  if (interviewStatus === 'completed') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-green-100 text-green-800">
        <div className="text-center">
          <p className="text-lg font-semibold">Interview Completed! Redirecting to report...</p>
        </div>
      </div>
    );
  }

  return (
    <SmoothPageTransition>
      <div className="min-h-screen flex flex-col">
      <Header />
      
      <div className="flex-grow flex bg-gray-50 relative">
        {/* Left Half: Question and Timers */}
        <div className="w-1/2 flex flex-col items-center justify-center p-8 bg-white shadow-lg">
          <div className="text-center mb-8">
            <div className="text-sm text-gray-600 mb-4">
              Interview in Progress
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Question {questionIndex} of {totalQuestions}
            </h2>
            {currentQuestion ? (
              <p className="text-4xl font-semibold text-gray-900 leading-tight">
                {currentQuestion.question_text}
              </p>
            ) : (
              <p className="text-xl text-gray-600">Fetching question...</p>
            )}
          </div>

          <div className="mt-8 text-center">
            {interviewType === 'system_design' ? (
              <>
                <p className="text-xl text-gray-700">Design your system architecture</p>
                <p className="text-lg text-gray-600 mt-2">Take your time to think through the design</p>
                <button
                  onClick={() => handleAnswerComplete(true)}
                  className="mt-6 px-8 py-3 bg-lime-500 text-white font-semibold rounded-lg shadow-md hover:bg-lime-600 transition-colors"
                >
                  Complete Design
                </button>
              </>
            ) : (
              <>
                {interviewStatus === 'preparing' && (
                  <>
                    <p className="text-xl text-gray-700">Prepare your answer:</p>
                    <p className="text-6xl font-bold text-lime-600">{prepTimeLeft}s</p>
                  </>
                )}
                {interviewStatus === 'answering' && (
                  <>
                    <p className="text-xl text-gray-700">Time to answer:</p>
                    <p className="text-6xl font-bold text-blue-600">{answerTimeLeft}s</p>
                    <button
                      onClick={() => handleAnswerComplete(true)}
                      className="mt-6 px-8 py-3 bg-lime-500 text-white font-semibold rounded-lg shadow-md hover:bg-lime-600 transition-colors"
                    >
                      End Answer Early
                    </button>
                  </>
                )}
              </>
            )}
          </div>
        </div>

        {/* Right Half: System Design Canvas or Camera Feed */}
        <div className="w-1/2 flex items-center justify-center bg-gray-800 relative">
          {interviewType === 'system_design' ? (
            <div className="w-full h-full flex">
              {/* System Design Canvas */}
              <div className="w-2/3 h-full">
                <SystemDesignCanvas
                  onScreenshot={handleScreenshot}
                  onProgressUpdate={handleProgressUpdate}
                  questionText={currentQuestion?.question_text || ''}
                />
              </div>
              {/* Chat Interface */}
              <div className="w-1/3 h-full border-l border-gray-300">
                <SystemDesignChat
                  onSendMessage={handleChatMessage}
                  messages={chatMessages}
                  isTyping={isTyping}
                />
              </div>
            </div>
          ) : (
            <>
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline
                muted
                className="w-full h-full object-cover rounded-lg shadow-lg"
                style={{ transform: 'scaleX(-1)' }} // Mirror the video for user comfort
                onLoadedMetadata={() => {
                  console.log('Video metadata loaded');
                  setCameraActive(true);
                }}
                onCanPlay={() => {
                  console.log('Video can play');
                  setCameraActive(true);
                }}
                onError={(e) => {
                  console.error('Video error:', e);
                  setCameraActive(false);
                }}
                onPlay={() => {
                  console.log('Video started playing');
                  setCameraActive(true);
                }}
              ></video>
              
              {/* Camera status indicator */}
              <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                ● Recording
              </div>
                  {/* Fallback message if camera doesn't work */}
                  {!cameraActive && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-90 text-white">
                      <div className="text-center">
                        <div className="text-6xl mb-4">📹</div>
                        <p className="text-lg font-semibold">Camera not available</p>
                        <p className="text-sm text-gray-300">Please allow camera access to continue</p>
                        <div className="mt-4 space-x-2">
                          <button 
                            onClick={startInterviewSession}
                            className="px-4 py-2 bg-lime-500 text-white rounded-lg hover:bg-lime-600"
                          >
                            Retry Camera Access
                          </button>
                          <button
                            onClick={() => {
                              console.log('=== CAMERA DEBUG INFO ===');
                              console.log('Video ref:', videoRef.current);
                              console.log('Media stream:', mediaStreamRef.current);
                              console.log('Camera active:', cameraActive);
                              console.log('Interview status:', interviewStatus);
                              console.log('Interview type:', interviewType);
                              console.log('Video srcObject:', videoRef.current?.srcObject);
                              console.log('Video readyState:', videoRef.current?.readyState);
                              console.log('getUserMedia available:', !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia));
                              console.log('========================');
                            }}
                            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                          >
                            Debug Info
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
            </>
          )}
          
        </div>
        
        {/* End Interview Button - Floating in Center Bottom */}
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 z-10">
          <button
            onClick={() => {
              if (window.confirm('Are you sure you want to end this interview? Your progress will be saved.')) {
                navigate('/interview/setup');
              }
            }}
            className="px-6 py-3 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-colors shadow-lg"
          >
            End Interview
          </button>
        </div>
      </div>
      
      {/* Voice Agent - Completely Invisible, Active Throughout Interview */}
      {voiceAgent && isVoiceAgentActive && (
        <div className="fixed inset-0 z-0 opacity-0 pointer-events-none">
          <VoiceAgent
            agentId={voiceAgent.agentId}
            agentName={voiceAgent.agentName}
            isActive={isVoiceAgentActive}
            onStart={() => console.log('Voice agent started for interview')}
            onEnd={stopVoiceAgent}
            onError={handleVoiceAgentError}
            onConversationIdReady={handleConversationIdReady}
            className="w-full"
          />
        </div>
      )}
      
      {/* Voice Agent Error Toast */}
      {voiceAgentError && (
        <div className="fixed top-4 right-4 z-50 bg-red-600 text-white px-4 py-3 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm">{voiceAgentError}</span>
            <button
              onClick={() => setVoiceAgentError(null)}
              className="ml-3 text-white hover:text-gray-200"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
    </SmoothPageTransition>
  );
}
