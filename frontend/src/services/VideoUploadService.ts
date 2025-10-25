/**
 * Video Upload Service
 * Handles uploading interview videos to Supabase Storage via backend API
 */

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

interface UploadResult {
  success: boolean;
  storage_path: string;
  video_url: string;
  size_bytes: number;
  size_mb: number;
}

class VideoUploadService {
  private baseUrl = 'http://localhost:8000/api/v1/video';

  /**
   * Upload interview video to Supabase Storage (silently, no download)
   */
  async uploadInterviewVideo(
    interviewId: string,
    videoBlob: Blob,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResult> {
    const token = localStorage.getItem('hirely_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    console.log('[VideoUpload] Starting upload...');
    console.log('[VideoUpload] Interview ID:', interviewId);
    console.log('[VideoUpload] Video size:', (videoBlob.size / 1024 / 1024).toFixed(2), 'MB');
    console.log('[VideoUpload] Video type:', videoBlob.type);

    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('interview_id', interviewId);
    formData.append('video', videoBlob, `interview_${interviewId}_${Date.now()}.webm`);

    try {
      // Upload using XMLHttpRequest for progress tracking
      const result = await this.uploadWithProgress(
        `${this.baseUrl}/upload`,
        formData,
        token,
        onProgress
      );

      console.log('[VideoUpload] ✅ Upload successful:', result);
      return result;
    } catch (error) {
      console.error('[VideoUpload] ❌ Upload failed:', error);
      throw error;
    }
  }

  /**
   * Upload with progress tracking using XMLHttpRequest
   */
  private uploadWithProgress(
    url: string,
    formData: FormData,
    token: string,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResult> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Progress tracking
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress: UploadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: Math.round((event.loaded / event.total) * 100)
          };
          onProgress(progress);
          console.log(`[VideoUpload] Progress: ${progress.percentage}%`);
        }
      });

      // Success
      xhr.addEventListener('load', () => {
        console.log('[VideoUpload] XHR load event - Status:', xhr.status);
        console.log('[VideoUpload] Response:', xhr.responseText.substring(0, 200));
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const result = JSON.parse(xhr.responseText);
            console.log('[VideoUpload] ✅ Upload successful, parsed result');
            resolve(result);
          } catch (error) {
            console.error('[VideoUpload] ❌ Failed to parse response:', error);
            reject(new Error('Failed to parse server response'));
          }
        } else {
          console.error('[VideoUpload] ❌ Upload failed with status:', xhr.status);
          try {
            const errorData = JSON.parse(xhr.responseText);
            console.error('[VideoUpload] Error details:', errorData);
            reject(new Error(errorData.detail || `Upload failed with status ${xhr.status}`));
          } catch {
            console.error('[VideoUpload] Could not parse error response');
            reject(new Error(`Upload failed with status ${xhr.status}`));
          }
        }
      });

      // Error
      xhr.addEventListener('error', (event) => {
        console.error('[VideoUpload] ❌ Network error during upload:', event);
        reject(new Error('Network error during upload'));
      });

      // Abort
      xhr.addEventListener('abort', () => {
        console.error('[VideoUpload] ❌ Upload aborted');
        reject(new Error('Upload aborted'));
      });

      // Send request
      console.log('[VideoUpload] Sending POST request to:', url);
      console.log('[VideoUpload] With Authorization header (first 20 chars):', token.substring(0, 20));
      xhr.open('POST', url);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);
      console.log('[VideoUpload] XHR request sent');
    });
  }

  /**
   * Get signed URL for accessing a video
   */
  async getVideoUrl(interviewId: string, expiresIn: number = 3600): Promise<string> {
    const token = localStorage.getItem('hirely_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    try {
      const response = await fetch(
        `${this.baseUrl}/download/${interviewId}?expires_in=${expiresIn}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get video URL');
      }

      const result = await response.json();
      return result.video_url;
    } catch (error) {
      console.error('[VideoUpload] Error getting video URL:', error);
      throw error;
    }
  }

  /**
   * Delete video from storage
   */
  async deleteVideo(interviewId: string): Promise<void> {
    const token = localStorage.getItem('hirely_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    try {
      const response = await fetch(`${this.baseUrl}/${interviewId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete video');
      }

      console.log('[VideoUpload] Video deleted successfully');
    } catch (error) {
      console.error('[VideoUpload] Error deleting video:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const videoUploadService = new VideoUploadService();
export type { UploadProgress, UploadResult };

