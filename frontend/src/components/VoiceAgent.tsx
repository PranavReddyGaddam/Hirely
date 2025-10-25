import { useState, useEffect, useRef } from 'react';
import { Conversation } from '@elevenlabs/client';

interface VoiceAgentProps {
  agentId: string;
  agentName: string;
  isActive: boolean;
  onStart?: () => void;
  onEnd?: () => void;
  onError?: (error: string) => void;
  className?: string;
}

export default function VoiceAgent({
  agentId,
  agentName,
  isActive,
  onStart,
  onEnd,
  onError,
  className = ''
}: VoiceAgentProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isCallActive, setIsCallActive] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [status, setStatus] = useState<string>('Initializing...');
  const [error, setError] = useState<string | null>(null);
  
  // ElevenLabs conversation refs
  const conversationRef = useRef<Conversation | null>(null);
  const conversationIdRef = useRef<string | null>(null);
  const isInitializingRef = useRef<boolean>(false);
  const isCleaningUpRef = useRef<boolean>(false);
  const hasInitializedRef = useRef<boolean>(false);

  // Effect to handle conversation lifecycle based on isActive
  useEffect(() => {
    console.log('[VoiceAgent] isActive changed to:', isActive);
    
    if (isActive) {
      // Start conversation
      startConversation();
    } else {
      // Cleanup conversation
      cleanupConversation();
    }
    
    // Cleanup on unmount
    return () => {
      console.log('[VoiceAgent] Component unmounting');
      cleanupConversation();
    };
  }, [isActive]);

  const startConversation = async () => {
    // Prevent multiple initializations
    if (conversationRef.current || isInitializingRef.current || isCleaningUpRef.current) {
      console.log('[VoiceAgent] Already have conversation or initializing/cleaning, skipping');
      return;
    }
    
    // Prevent React StrictMode double initialization
    if (hasInitializedRef.current && conversationRef.current) {
      console.log('[VoiceAgent] Already initialized in this render cycle');
      return;
    }

    try {
      isInitializingRef.current = true;
      hasInitializedRef.current = true;
      setStatus('Connecting to interviewer...');
      console.log('[VoiceAgent] Starting session for agent:', agentId);
        
      // Initialize ElevenLabs conversation with enhanced noise reduction
      const conversation = await Conversation.startSession({
        agentId: agentId,
        connectionType: 'websocket',
        onConnect: () => {
          console.log('[VoiceAgent] Connected to ElevenLabs');
          setIsConnected(true);
          setIsCallActive(true);
          setStatus('Connected - Speak naturally!');
          onStart?.();
        },
        onDisconnect: () => {
          console.log('[VoiceAgent] Disconnected from ElevenLabs');
          setIsConnected(false);
          setIsCallActive(false);
          setStatus('Disconnected');
          onEnd?.();
        },
        onMessage: (message: any) => {
          // Message handler - not used for transcript
          console.log('[VoiceAgent] Message received:', message.type);
        },
        onError: (error: any) => {
          console.error('[VoiceAgent] Error:', error);
          const errorMessage = error?.message || 'An error occurred during the call';
          setError(errorMessage);
          setStatus('Error');
          onError?.(errorMessage);
        },
      });
      
      console.log('[VoiceAgent] Session created successfully');
      
      // Store conversation
      conversationRef.current = conversation;
      
      // Store conversation ID
      try {
        const id = conversation.getId();
        if (id) {
          conversationIdRef.current = id;
          console.log('[VoiceAgent] Conversation ID:', id);
        }
      } catch (err) {
        console.log('[VoiceAgent] Conversation ID not yet available');
      }
      
    } catch (err: any) {
      console.error('[VoiceAgent] Failed to initialize:', err);
      const errorMessage = err.message || 'Failed to start call. Please check your microphone permissions.';
      setError(errorMessage);
      setStatus('Failed');
      onError?.(errorMessage);
    } finally {
      isInitializingRef.current = false;
    }
  };

  const cleanupConversation = async () => {
    // Prevent multiple simultaneous cleanups
    if (isCleaningUpRef.current) {
      console.log('[VoiceAgent] Already cleaning up, skipping');
      return;
    }
    
    // Check if there's anything to cleanup
    if (!conversationRef.current) {
      console.log('[VoiceAgent] No conversation to cleanup');
      return;
    }
    
    isCleaningUpRef.current = true;
    const conversation = conversationRef.current;
    
    // Clear refs immediately to prevent reuse
    conversationRef.current = null;
    conversationIdRef.current = null;
    hasInitializedRef.current = false;
    
    console.log('[VoiceAgent] Starting cleanup...');
    
    try {
      console.log('[VoiceAgent] Calling endSession...');
      await conversation.endSession();
      console.log('[VoiceAgent] Session ended successfully');
    } catch (err) {
      console.error('[VoiceAgent] Error during cleanup:', err);
    } finally {
      isCleaningUpRef.current = false;
      
      // Reset all state
      setIsCallActive(false);
      setIsConnected(false);
      setError(null);
      setIsMuted(false);
      setStatus('Initializing...');
    }
  };

  const handleEndCall = async () => {
    console.log('[VoiceAgent] handleEndCall called');
    await cleanupConversation();
    onEnd?.();
  };

  const toggleMute = () => {
    if (conversationRef.current) {
      const newMutedState = !isMuted;
      conversationRef.current.setMicMuted(newMutedState);
      setIsMuted(newMutedState);
    }
  };

  if (!isActive) return null;

  return (
    <div className={`bg-gray-900 rounded-2xl border border-gray-700 shadow-2xl ${className}`}>
      {/* Header */}
      <div className="relative p-4 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">{agentName}</h3>
            <p className="text-gray-400 text-sm">Voice Interview</p>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="p-4">
        <div className="flex items-center justify-center mb-4">
          {isConnected ? (
            <div className="flex items-center gap-2 text-green-400">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">{status}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-yellow-400">
              <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">{status}</span>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-900 bg-opacity-30 border border-red-500 rounded-lg">
            <p className="text-red-300 text-xs">{error}</p>
          </div>
        )}

        {/* Call Instructions */}
        <div className="mb-4 text-center">
          <p className="text-gray-300 text-sm mb-1">Speak naturally with the interviewer</p>
          <p className="text-gray-500 text-xs">Enhanced noise reduction is active</p>
        </div>

        {/* Call Controls */}
        <div className="flex justify-center gap-3">
          <button
            onClick={toggleMute}
            disabled={!isCallActive}
            className={`p-3 rounded-full transition-colors ${
              isMuted
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-gray-700 hover:bg-gray-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            aria-label={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? (
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5l14 14" />
              </svg>
            ) : (
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            )}
          </button>
          
          <button
            onClick={handleEndCall}
            className="p-3 rounded-full bg-red-600 hover:bg-red-700 transition-colors"
            aria-label="End Call"
          >
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M3 3l3.09 3.09A2 2 0 006 8.83v6.34a2 2 0 001.91 1.74L11 19h2a2 2 0 002-2v-6.34a2 2 0 001.91-1.74L21 3" />
            </svg>
          </button>
        </div>

        {/* Instructions */}
        <p className="text-center text-gray-400 text-xs mt-3">
          {isCallActive 
            ? 'Speak naturally. Background noise is automatically filtered.'
            : 'Please wait while we connect you...'}
        </p>
      </div>
    </div>
  );
}
