import { API_BASE_URL } from '../config';

export interface VideoJobStatus {
  job_id: string;
  status: string;
  message: string;
  percent: number;
  timestamp?: number;
  error?: string;
  result?: any;
}

export class VideoService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL || 'http://localhost:8000';
  }

  /**
   * Upload and process a video file
   * @param file Video file to upload
   * @param onProgress Progress callback
   * @returns Promise with final job result
   */
  async processVideo(file: File, onProgress?: (status: VideoJobStatus) => void): Promise<any> {
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file);

      // Start the upload
      const response = await fetch(`${this.baseUrl}/video/process`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      const jobId = data.job_id;

      if (onProgress) {
        // Start SSE for progress updates
        this.connectToProgressEvents(jobId, onProgress);
      }

      return data;
    } catch (error) {
      console.error('Video processing error:', error);
      throw error;
    }
  }

  /**
   * Process a video from URL
   * @param url Video URL
   * @param onProgress Progress callback
   * @returns Promise with final job result
   */
  async processVideoUrl(url: string, onProgress?: (status: VideoJobStatus) => void): Promise<any> {
    try {
      // Create form data
      const formData = new FormData();
      formData.append('url', url);

      // Start the upload
      const response = await fetch(`${this.baseUrl}/video/process`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      const jobId = data.job_id;

      if (onProgress) {
        // Start SSE for progress updates
        this.connectToProgressEvents(jobId, onProgress);
      }

      return data;
    } catch (error) {
      console.error('Video processing error:', error);
      throw error;
    }
  }

  /**
   * Get the current status of a video job
   * @param jobId Job ID to check
   * @returns Promise with job status
   */
  async getJobStatus(jobId: string): Promise<VideoJobStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/video/status/${jobId}`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error (${response.status}): ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking job status:', error);
      throw error;
    }
  }

  /**
   * Connect to SSE events for progress updates
   * @param jobId Job ID to track
   * @param onProgress Callback function for progress updates
   */
  private connectToProgressEvents(jobId: string, onProgress: (status: VideoJobStatus) => void): void {
    // Close any existing connection
    this.closeSSEConnection();

    const eventSource = new EventSource(`${this.baseUrl}/video/progress/${jobId}`);
    
    // Store the event source globally to close it later
    (window as any).__videoSSEConnection = eventSource;

    // Handle incoming messages
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as VideoJobStatus;
        
        // Call the progress callback
        onProgress(data);
        
        // If processing is complete or there was an error, close the connection
        if (data.status === 'complete' || data.status === 'error' || data.status === 'closed') {
          this.closeSSEConnection();
        }
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    // Handle connection open
    eventSource.onopen = () => {
      console.log('SSE connection opened for job', jobId);
    };

    // Handle errors
    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      this.closeSSEConnection();
      
      // Notify caller about the error
      onProgress({
        job_id: jobId,
        status: 'error',
        message: 'Connection to server lost',
        percent: 0,
        error: 'SSE connection error'
      });
    };
  }

  /**
   * Close any open SSE connections
   */
  private closeSSEConnection(): void {
    if ((window as any).__videoSSEConnection) {
      (window as any).__videoSSEConnection.close();
      (window as any).__videoSSEConnection = null;
    }
  }
} 