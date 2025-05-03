"use client";

import React, { useState } from "react";
import { Button } from "./Button";
import { FeatherX, FeatherClipboard } from "@subframe/core";
import { IconButton } from "./IconButton";
import { SearchResult } from "../../types/sourceTrace";

interface ShareModalProps {
  originalSource: SearchResult;
  viralPoints: SearchResult[];
  onClose: () => void;
}

export const ShareModal: React.FC<ShareModalProps> = ({
  originalSource,
  viralPoints,
  onClose,
}) => {
  const [includeVirality, setIncludeVirality] = useState(false);
  const [shareText, setShareText] = useState(
    `This has been traced to an earlier post - "${originalSource.title}" by ${originalSource.platform}`
  );

  const handleToggleVirality = () => {
    setIncludeVirality(!includeVirality);
    if (!includeVirality) {
      const viralUrls = viralPoints
        .slice(0, 3)
        .map((point) => `https://${point.platform.toLowerCase()}.com/post/${point.title.replace(/\s+/g, '-')}`)
        .join(", ");
      setShareText(
        `${shareText}\n\nOther posts include ${viralUrls}`
      );
    } else {
      setShareText(
        `This has been traced to an earlier post - "${originalSource.title}" by ${originalSource.platform}`
      );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="flex w-[500px] flex-col items-start gap-4 rounded-md border border-solid border-neutral-border bg-default-background p-6">
        <div className="flex w-full items-center justify-between">
          <span className="text-heading-2 font-heading-2 text-default-font">
            Share Trace
          </span>
          <IconButton
            icon={<FeatherX />}
            onClick={onClose}
          />
        </div>
        <div className="flex w-full flex-col items-start gap-4">
          <textarea
            className="h-32 w-full rounded-md border border-solid border-neutral-border bg-default-background p-3 text-body font-body text-default-font"
            value={shareText}
            onChange={(e) => setShareText(e.target.value)}
          />
          <div className="flex w-full items-center gap-2">
            <label className="text-body font-body text-default-font">
              Include virality?
            </label>
            <button
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                includeVirality ? "bg-brand-600" : "bg-neutral-200"
              }`}
              onClick={handleToggleVirality}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  includeVirality ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
          <div className="flex w-full items-center justify-between">
            <Button
              variant="neutral-tertiary"
              onClick={onClose}
            >
              Cancel
            </Button>
            <Button
              variant="brand-primary"
              icon={<FeatherClipboard />}
              onClick={() => navigator.clipboard.writeText(shareText)}
            >
              Copy
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}; 