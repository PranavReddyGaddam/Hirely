/**
 * CV Tracking Service
 * Handles frame capture and communication with backend CV analysis
 */

export interface CVMetrics {
  expression: string;
  confidence: number;
  face_detected?: boolean;
  ear_avg: number;
  mar: number;
  smile_intensity: number;
  blink_rate: number;
  stress_level: string;
  head_yaw: number;
  head_pitch: number;
  head_roll: number;
  head_direction: string;
  is_looking_at_camera: boolean;
  posture_status: string;
  neck_angle: number;
  torso_angle: number;
  is_slouching: boolean;
  face_touching: boolean;
  hand_fidgeting: boolean;
  excessive_gesturing: boolean;
  attention_score: number;
  is_engaged: boolean;
  is_distracted: boolean;
}

class CVTrackingService {
  private interviewId: string | null = null;
  private sessionActive = false;
  private frameInterval: number | null = null;
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private onMetricsUpdate: ((metrics: CVMetrics) => void) | null = null;

  /**
   * Start CV tracking session
   */
  async startSession(interviewId: string, videoElement: HTMLVideoElement): Promise<void> {
    this.interviewId = interviewId;
    this.videoElement = videoElement;
    this.sessionActive = true;

    // Create canvas for frame capture
    this.canvasElement = document.createElement('canvas');
    this.canvasElement.width = 640;
    this.canvasElement.height = 480;

    try {
      // Initialize CV session on backend
      const formData = new FormData();
      formData.append('interview_id', interviewId);

      const response = await fetch('/api/v1/cv/start-session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('hirely_token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to start CV session');
      }

      const result = await response.json();
      console.log('[CV Tracking] Session started:', result);

      // Start frame capture loop (5 FPS = every 200ms)
      this.startFrameCapture();

    } catch (error) {
      console.error('[CV Tracking] Error starting session:', error);
      throw error;
    }
  }

  /**
   * Start capturing and sending frames
   */
  private startFrameCapture(): void {
    console.log('[CV Tracking] Starting frame capture at 5 FPS');
    
    this.frameInterval = window.setInterval(async () => {
      if (!this.sessionActive || !this.videoElement || !this.canvasElement) {
        console.warn('[CV Tracking] Frame capture skipped - session inactive or elements missing');
        return;
      }

      try {
        // Check video is playing
        if (this.videoElement.paused || this.videoElement.readyState < 2) {
          console.warn('[CV Tracking] Video not ready or paused');
          return;
        }

        // Capture frame from video
        const ctx = this.canvasElement.getContext('2d');
        if (!ctx) {
          console.error('[CV Tracking] Cannot get canvas context');
          return;
        }

        ctx.drawImage(
          this.videoElement,
          0, 0,
          this.canvasElement.width,
          this.canvasElement.height
        );

        // Convert to blob
        this.canvasElement.toBlob(async (blob) => {
          if (!blob || !this.sessionActive) return;

          // Send to backend
          const formData = new FormData();
          formData.append('frame', blob, 'frame.jpg');
          formData.append('interview_id', this.interviewId!);

          const response = await fetch('/api/v1/cv/process-frame', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('hirely_token')}`
            },
            body: formData
          });

          if (response.ok) {
            const result = await response.json();
            console.log('[CV Tracking] Frame processed:', result);
            
            // Update metrics
            if (this.onMetricsUpdate && result.metrics) {
              this.onMetricsUpdate(result.metrics);
            } else {
              console.warn('[CV Tracking] No callback or metrics in response');
            }
          } else {
            console.error('[CV Tracking] Frame processing failed:', response.status, await response.text());
          }
        }, 'image/jpeg', 0.8);

      } catch (error) {
        console.error('[CV Tracking] Error processing frame:', error);
      }
    }, 200); // 5 FPS
  }

  /**
   * Stop CV tracking and get analysis
   */
  async endSession(): Promise<any> {
    if (!this.sessionActive || !this.interviewId) {
      console.warn('[CV Tracking] No active session to end');
      return null;
    }

    // Stop frame capture
    if (this.frameInterval) {
      clearInterval(this.frameInterval);
      this.frameInterval = null;
    }

    this.sessionActive = false;

    try {
      // End session on backend
      const formData = new FormData();
      formData.append('interview_id', this.interviewId);

      const response = await fetch('/api/v1/cv/end-session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('hirely_token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to end CV session');
      }

      const result = await response.json();
      console.log('[CV Tracking] Session ended:', result);

      // Cleanup
      this.interviewId = null;
      this.videoElement = null;
      this.canvasElement = null;

      return result;

    } catch (error) {
      console.error('[CV Tracking] Error ending session:', error);
      throw error;
    }
  }

  /**
   * Set callback for metrics updates
   */
  setMetricsCallback(callback: (metrics: CVMetrics) => void): void {
    this.onMetricsUpdate = callback;
  }

  /**
   * Check if session is active
   */
  isActive(): boolean {
    return this.sessionActive;
  }
}

export const cvTrackingService = new CVTrackingService();
