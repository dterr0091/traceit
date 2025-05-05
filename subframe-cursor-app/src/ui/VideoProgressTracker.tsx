import React, { useEffect, useState } from 'react';
import { VideoJobStatus } from '../services/videoService';

interface VideoProgressTrackerProps {
  jobStatus: VideoJobStatus | null;
  onComplete?: (result: any) => void;
}

const VideoProgressTracker: React.FC<VideoProgressTrackerProps> = ({ 
  jobStatus, 
  onComplete 
}) => {
  const [statusMessage, setStatusMessage] = useState<string>('Initializing...');
  const [progress, setProgress] = useState<number>(0);
  const [isComplete, setIsComplete] = useState<boolean>(false);
  const [hasError, setHasError] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    if (!jobStatus) return;

    // Update component state based on job status
    setProgress(jobStatus.percent || 0);
    setStatusMessage(jobStatus.message || 'Processing...');

    // Check for completion or error
    if (jobStatus.status === 'complete') {
      setIsComplete(true);
      if (onComplete && jobStatus.result) {
        onComplete(jobStatus.result);
      }
    } else if (jobStatus.status === 'error') {
      setHasError(true);
      setErrorMessage(jobStatus.message || 'An error occurred during processing');
    }
  }, [jobStatus, onComplete]);

  // Status bar color based on state
  const getStatusBarColor = () => {
    if (hasError) return 'bg-red-500';
    if (isComplete) return 'bg-green-500';
    return 'bg-blue-500';
  };

  // Return empty div if no job status
  if (!jobStatus) return null;

  return (
    <div className="w-full max-w-md mx-auto bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-medium mb-2">
        {isComplete ? 'Processing Complete' : hasError ? 'Processing Error' : 'Processing Video...'}
      </h3>
      
      <div className="mb-3">
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div 
            className={`h-4 rounded-full ${getStatusBarColor()}`} 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="text-right text-sm text-gray-600 mt-1">
          {progress}%
        </div>
      </div>
      
      <div className="text-sm text-gray-700">
        {hasError ? (
          <div className="text-red-500">{errorMessage}</div>
        ) : (
          <div>{statusMessage}</div>
        )}
      </div>
      
      {isComplete && (
        <div className="mt-3 text-green-600">
          Analysis complete! View results below.
        </div>
      )}
    </div>
  );
};

export default VideoProgressTracker; 