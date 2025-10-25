import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import { useAuth } from '../hooks/useAuth';
import { SmoothPageTransition, SkeletonCard, SkeletonText, LoadingSpinner } from '../components/SkeletonLoader';

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
      // Cleanup media stream on component unmount
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isAuthenticated, authLoading, interviewId, navigate]);

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
  }, [interviewStatus, currentQuestion]);

  const startInterviewSession = async () => {
    setInterviewStatus('loading');
    setError(null);
    try {
      console.log('Requesting camera access...');
      
      // Request camera access
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }, 
        audio: true 
      });
      
      console.log('Camera stream obtained:', stream);
      console.log('Video tracks:', stream.getVideoTracks());
      console.log('Audio tracks:', stream.getAudioTracks());
      
      // Store the stream first
      mediaStreamRef.current = stream;
      console.log('Stream stored in ref');
      
      // Wait for video element to be ready, then assign stream
      const assignStreamToVideo = () => {
        if (videoRef.current) {
          console.log('Video ref is ready, assigning stream...');
          videoRef.current.srcObject = stream;
          
          // Wait for video to load
          videoRef.current.onloadedmetadata = () => {
            console.log('Video metadata loaded');
            videoRef.current?.play().then(() => {
              console.log('Video started playing');
              setCameraActive(true);
            }).catch((playErr) => {
              console.error('Error playing video:', playErr);
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

      // Fetch the first question
      await fetchNextQuestion();

    } catch (err) {
      console.error('Error starting interview session:', err);
      setError('Failed to access camera/microphone or fetch interview data. Please ensure permissions are granted.');
      setInterviewStatus('error');
    }
  };

  const fetchNextQuestion = async () => {
    // Don't set loading status to avoid camera reinitialization
    setError(null);
    try {
      const token = localStorage.getItem('hirely_token');
      const response = await fetch(`http://localhost:8000/api/v1/interviews/${interviewId}/next_question`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.question) {
          setCurrentQuestion(data.question);
          setQuestionIndex(data.question_index);
          setTotalQuestions(data.total_questions);
          setPrepTimeLeft(20); // Reset prep timer
          setInterviewStatus('preparing');
        } else {
          // No more questions, interview completed
          setInterviewStatus('completed');
          navigate(`/interview/${interviewId}/report`); // Redirect to report page
        }
      } else if (response.status === 404) {
        // No more questions available - interview completed
        setInterviewStatus('completed');
        navigate(`/interview/${interviewId}/report`); // Redirect to report page
      } else {
        const errorData = await response.json();
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
      <div className="flex-grow flex bg-gray-50">
        {/* Left Half: Question and Timers */}
        <div className="w-1/2 flex flex-col items-center justify-center p-8 bg-white shadow-lg">
          <div className="text-center mb-8">
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
          </div>
        </div>

        {/* Right Half: Camera Feed */}
        <div className="w-1/2 flex items-center justify-center bg-gray-800 relative">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
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
          <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium">
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
                      console.log('Debug info:');
                      console.log('Video ref:', videoRef.current);
                      console.log('Media stream:', mediaStreamRef.current);
                      console.log('Camera active:', cameraActive);
                      console.log('Video srcObject:', videoRef.current?.srcObject);
                      console.log('Video readyState:', videoRef.current?.readyState);
                    }}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                  >
                    Debug Info
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    </SmoothPageTransition>
  );
}
