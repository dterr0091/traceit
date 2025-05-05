import React, { useState } from 'react';
import VideoUploader from '../ui/VideoUploader';

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

  const handleVideoProcessed = (result: VideoAnalysisResult) => {
    setAnalysisResult(result);
  };

  const renderOrigin = (origin: any, type: string) => {
    if (!origin) return null;
    
    return (
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">{type} Origin</h3>
        <div className="text-sm">
          <p><span className="font-medium">Source:</span> {origin.source || 'Unknown'}</p>
          <p><span className="font-medium">Channel:</span> {origin.channelId || 'Unknown'}</p>
          <p><span className="font-medium">Published:</span> {origin.publishedAt || 'Unknown'}</p>
          <p><span className="font-medium">URL:</span> {
            origin.url ? (
              <a 
                href={origin.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                {origin.url}
              </a>
            ) : 'Unknown'
          }</p>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Video Analysis</h1>
      <div className="mb-8">
        <VideoUploader onVideoProcessed={handleVideoProcessed} />
      </div>
      
      {analysisResult && (
        <div className="bg-white p-5 rounded-lg shadow-lg">
          <h2 className="text-xl font-bold mb-4">Analysis Results</h2>
          
          {analysisResult.is_composite ? (
            <div className="mb-4 p-3 bg-yellow-100 text-yellow-800 rounded">
              This appears to be a composite video with different audio and visual origins.
            </div>
          ) : (
            <div className="mb-4 p-3 bg-green-100 text-green-800 rounded">
              This appears to be an original video from a single source.
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderOrigin(analysisResult.origins.visual, 'Visual')}
            {renderOrigin(analysisResult.origins.audio, 'Audio')}
          </div>
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Confidence Scores</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium">Visual Confidence</h4>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-blue-600 h-2.5 rounded-full" 
                    style={{ width: `${(analysisResult.confidence.visual || 0) * 100}%` }}
                  ></div>
                </div>
                <p className="text-right text-sm text-gray-600 mt-1">
                  {(analysisResult.confidence.visual || 0).toFixed(2)}
                </p>
              </div>
              
              <div>
                <h4 className="font-medium">Audio Confidence</h4>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-blue-600 h-2.5 rounded-full" 
                    style={{ width: `${(analysisResult.confidence.audio || 0) * 100}%` }}
                  ></div>
                </div>
                <p className="text-right text-sm text-gray-600 mt-1">
                  {(analysisResult.confidence.audio || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-2">Video Metadata</h3>
            <pre className="bg-gray-100 p-4 rounded overflow-x-auto text-xs">
              {JSON.stringify(analysisResult.metadata, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoAnalysisPage; 