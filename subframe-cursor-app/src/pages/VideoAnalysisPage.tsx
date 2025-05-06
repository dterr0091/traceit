import React, { useState } from 'react';
import VideoUploader from '../ui/VideoUploader';
import CompositeMediaDisplay from '../ui/CompositeMediaDisplay';

interface VideoAnalysisResult {
  job_id: string;
  metadata: any;
  origins: {
    audio?: any;
    visual?: any;
  };
  is_composite: boolean;
  confidence: {
    audio: number;
    visual: number;
  };
  hash: string;
}

const VideoAnalysisPage: React.FC = () => {
  const [analysisResult, setAnalysisResult] = useState<VideoAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleVideoProcessed = (result: VideoAnalysisResult) => {
    setAnalysisResult(result);
    setIsLoading(false);
  };

  const handleVideoUploadStart = () => {
    setIsLoading(true);
    setAnalysisResult(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Video Analysis</h1>
      <div className="mb-8">
        <VideoUploader 
          onVideoProcessed={handleVideoProcessed} 
          onUploadStart={handleVideoUploadStart}
        />
      </div>
      
      {isLoading && (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <span className="ml-3">Processing video...</span>
        </div>
      )}
      
      {analysisResult && (
        <div className="bg-white p-5 rounded-lg shadow-lg">
          <h2 className="text-xl font-bold mb-4">Analysis Results</h2>
          
          <CompositeMediaDisplay 
            audioOrigin={analysisResult.origins.audio}
            visualOrigin={analysisResult.origins.visual}
            isComposite={analysisResult.is_composite}
            audioConfidence={analysisResult.confidence.audio}
            visualConfidence={analysisResult.confidence.visual}
          />
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Video Metadata</h3>
            <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-xs">
              {JSON.stringify(analysisResult.metadata, null, 2)}
            </pre>
          </div>
          
          <div className="mt-4 text-xs text-gray-500">
            <p>Job ID: {analysisResult.job_id}</p>
            <p>Content Hash: {analysisResult.hash}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoAnalysisPage; 