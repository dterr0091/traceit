import React, { useState, useRef, ChangeEvent } from 'react';
import { VideoService, VideoJobStatus } from '../services/videoService';
import VideoProgressTracker from './VideoProgressTracker';

interface VideoUploaderProps {
  onVideoProcessed?: (result: any) => void;
}

const VideoUploader: React.FC<VideoUploaderProps> = ({ onVideoProcessed }) => {
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string>('');
  const [jobStatus, setJobStatus] = useState<VideoJobStatus | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [uploadType, setUploadType] = useState<'file' | 'url'>('file');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoService = new VideoService();

  const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
    setUploadError('');
    
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Check file type
    if (!file.type.startsWith('video/')) {
      setUploadError('Only video files are accepted');
      return;
    }
    
    // Check file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      setUploadError('File size must be less than 50MB');
      return;
    }
    
    // Upload file
    await handleUpload(file);
  };
  
  const handleUrlSubmit = async () => {
    setUploadError('');
    
    if (!videoUrl) {
      setUploadError('Please enter a video URL');
      return;
    }
    
    // Validate URL (very basic validation)
    if (!videoUrl.startsWith('http')) {
      setUploadError('Please enter a valid URL');
      return;
    }
    
    // Process from URL
    await handleUrlUpload(videoUrl);
  };
  
  const handleUpload = async (file: File) => {
    try {
      setIsUploading(true);
      setJobStatus(null);
      
      // Start video upload and processing
      const response = await videoService.processVideo(file, (status) => {
        // Update job status for progress tracking
        setJobStatus(status);
      });
      
      // Initial response includes job_id
      console.log('Video processing started:', response);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError('Failed to upload video');
    } finally {
      setIsUploading(false);
    }
  };
  
  const handleUrlUpload = async (url: string) => {
    try {
      setIsUploading(true);
      setJobStatus(null);
      
      // Start video processing from URL
      const response = await videoService.processVideoUrl(url, (status) => {
        // Update job status for progress tracking
        setJobStatus(status);
      });
      
      // Initial response includes job_id
      console.log('Video processing started:', response);
      
    } catch (error) {
      console.error('URL processing error:', error);
      setUploadError('Failed to process video URL');
    } finally {
      setIsUploading(false);
    }
  };
  
  const handleComplete = (result: any) => {
    if (onVideoProcessed) {
      onVideoProcessed(result);
    }
  };
  
  const resetUpload = () => {
    setJobStatus(null);
    setUploadError('');
    setVideoUrl('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto bg-white p-5 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4">Video Analysis</h2>
      
      {!jobStatus ? (
        <>
          <div className="mb-4">
            <div className="flex space-x-4 mb-4">
              <button
                className={`px-4 py-2 rounded ${uploadType === 'file' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                onClick={() => setUploadType('file')}
              >
                Upload File
              </button>
              <button
                className={`px-4 py-2 rounded ${uploadType === 'url' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                onClick={() => setUploadType('url')}
              >
                YouTube URL
              </button>
            </div>
            
            {uploadType === 'file' ? (
              <label className="block">
                <span className="text-gray-700">Select Video File</span>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="video/*"
                  onChange={handleFileChange}
                  disabled={isUploading}
                  className="block w-full mt-1 border-gray-300 rounded shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Maximum file size: 50MB. Supported formats: MP4, MOV, AVI, etc.
                </p>
              </label>
            ) : (
              <div>
                <label className="block">
                  <span className="text-gray-700">Video URL</span>
                  <input
                    type="text"
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                    disabled={isUploading}
                    placeholder="https://example.com/video.mp4 or YouTube URL"
                    className="block w-full mt-1 border-gray-300 rounded shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                </label>
                <button
                  onClick={handleUrlSubmit}
                  disabled={isUploading || !videoUrl}
                  className="mt-3 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {isUploading ? 'Processing...' : 'Analyze Video'}
                </button>
              </div>
            )}
          </div>
          
          {uploadError && (
            <div className="text-red-500 mb-4">
              {uploadError}
            </div>
          )}
        </>
      ) : (
        <>
          <VideoProgressTracker
            jobStatus={jobStatus}
            onComplete={handleComplete}
          />
          
          <button
            onClick={resetUpload}
            className="mt-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            Start New Analysis
          </button>
        </>
      )}
    </div>
  );
};

export default VideoUploader; 