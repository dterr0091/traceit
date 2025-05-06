import React from 'react';
import { formatDistanceToNow } from 'date-fns';

interface OriginType {
  found: boolean;
  confidence: number;
  matching_frames?: number;
  hit?: {
    id: string;
    url: string;
    title: string;
    channel_id: string;
    timestamp: string;
  };
}

interface CompositeMediaDisplayProps {
  audioOrigin: OriginType | null;
  visualOrigin: OriginType | null;
  isComposite: boolean;
  audioConfidence: number;
  visualConfidence: number;
}

const CompositeMediaDisplay: React.FC<CompositeMediaDisplayProps> = ({
  audioOrigin,
  visualOrigin,
  isComposite,
  audioConfidence,
  visualConfidence
}) => {
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' (' + formatDistanceToNow(date, { addSuffix: true }) + ')';
    } catch (e) {
      return 'Unknown date';
    }
  };

  const renderOriginCard = (origin: OriginType | null, type: 'audio' | 'visual') => {
    if (!origin || !origin.found || !origin.hit) {
      return (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold">{type === 'audio' ? 'Audio' : 'Visual'} Origin</h3>
          <p className="text-gray-500">No origin information available</p>
        </div>
      );
    }

    const { hit, confidence, matching_frames } = origin;
    
    return (
      <div className="p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-semibold">
            {type === 'audio' ? '🔊 Audio' : '📹 Visual'} Origin
          </h3>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded">
            {(confidence * 100).toFixed(1)}% match
          </span>
        </div>
        
        <h4 className="text-base font-medium mt-3 mb-1">{hit.title || 'Untitled'}</h4>
        
        <div className="space-y-2 text-sm mt-3">
          {hit.channel_id && (
            <div className="flex">
              <span className="font-medium w-24">Channel:</span>
              <span>{hit.channel_id}</span>
            </div>
          )}
          
          {hit.timestamp && (
            <div className="flex">
              <span className="font-medium w-24">Published:</span>
              <span>{formatDate(hit.timestamp)}</span>
            </div>
          )}
          
          {type === 'visual' && matching_frames !== undefined && (
            <div className="flex">
              <span className="font-medium w-24">Frame Matches:</span>
              <span>{matching_frames} out of 3</span>
            </div>
          )}
          
          {hit.url && (
            <div className="mt-3">
              <a 
                href={hit.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1.5 text-sm text-blue-700 bg-blue-50 hover:bg-blue-100 rounded"
              >
                Visit Source
                <svg className="w-3.5 h-3.5 ml-2" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
                  <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5h12m0 0L9 1m4 4L9 9"/>
                </svg>
              </a>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full">
      {isComposite && (
        <div className="mb-4 p-3 bg-amber-50 border-l-4 border-amber-500 text-amber-700">
          <div className="font-medium">⚠️ Composite Media Detected</div>
          <p className="text-sm">This video appears to combine audio and visual content from different sources.</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {renderOriginCard(visualOrigin, 'visual')}
        {renderOriginCard(audioOrigin, 'audio')}
      </div>
      
      {isComposite && visualOrigin?.found && audioOrigin?.found && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-md font-semibold mb-2">Timeline</h3>
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-0 w-1 bg-gray-200 h-full rounded"></div>
            
            {/* Timeline items */}
            <div className="ml-6 space-y-4">
              {[visualOrigin, audioOrigin]
                .filter(origin => origin?.hit?.timestamp)
                .sort((a, b) => {
                  const dateA = new Date(a?.hit?.timestamp || '');
                  const dateB = new Date(b?.hit?.timestamp || '');
                  return dateA.getTime() - dateB.getTime();
                })
                .map((origin, index) => (
                  <div key={index} className="relative">
                    {/* Timeline dot */}
                    <div className="absolute -left-9 mt-1.5 w-4 h-4 rounded-full bg-blue-500 border-2 border-white"></div>
                    <div>
                      <h4 className="text-sm font-semibold">
                        {origin === visualOrigin ? 'Visual content' : 'Audio content'} published
                      </h4>
                      <p className="text-xs text-gray-500">
                        {formatDate(origin?.hit?.timestamp || '')}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompositeMediaDisplay; 