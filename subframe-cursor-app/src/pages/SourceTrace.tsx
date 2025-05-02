"use client";

import React, { useState, useRef } from "react";
import { DefaultPageLayout } from "@/ui/layouts/DefaultPageLayout";
import { TextField } from "@/ui/components/TextField";
import { FeatherSearch } from "@subframe/core";
import { FeatherXCircle } from "@subframe/core";
import { Button } from "@/ui/components/Button";
import { Badge } from "@/ui/components/Badge";
import { FeatherGlobe } from "@subframe/core";
import { FeatherChevronDown } from "@subframe/core";
import { IconButton } from "@/ui/components/IconButton";
import { FeatherShare2 } from "@subframe/core";
import { Avatar } from "@/ui/components/Avatar";
import { FeatherClock } from "@subframe/core";
import { Table } from "@/ui/components/Table";
import { FeatherPlus } from "@subframe/core";
import { FeatherThumbsUp } from "@subframe/core";
import { FeatherImage } from "@subframe/core";
import { FeatherLoader } from "@subframe/core";

interface SearchResult {
  title: string;
  platform: string;
  timestamp: string;
  viralityScore: 'High' | 'Medium' | 'Low';
  platformIcon: string;
}

interface SearchState {
  isLoading: boolean;
  currentStep: string;
  error: string | null;
  results: SearchResult[] | null;
}

function SourceTrace() {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [uploadedImages, setUploadedImages] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [searchState, setSearchState] = useState<SearchState>({
    isLoading: false,
    currentStep: '',
    error: null,
    results: null
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const mockSearch = async (query: string, images: string[]) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock response
    return [
      {
        title: "Tech Workforce Reduction",
        platform: "Twitter",
        timestamp: "March 15, 9:00 AM",
        viralityScore: "High" as const,
        platformIcon: "https://images.unsplash.com/photo-1611162617474-5b21e879e113"
      },
      {
        title: "AI Impact on Tech Jobs",
        platform: "Reddit",
        timestamp: "March 15, 10:30 AM",
        viralityScore: "Medium" as const,
        platformIcon: "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0"
      },
      {
        title: "Industry Workforce Trends",
        platform: "Facebook",
        timestamp: "March 15, 2:15 PM",
        viralityScore: "Low" as const,
        platformIcon: "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb"
      }
    ];
  };

  const handleSearch = async () => {
    if (!searchQuery && uploadedImages.length === 0) {
      setSearchState(prev => ({ ...prev, error: "Please enter a search query or upload an image" }));
      return;
    }

    setSearchState({
      isLoading: true,
      currentStep: "Analyzing input...",
      error: null,
      results: null
    });

    try {
      // Simulate different steps
      const steps = [
        "Analyzing input...",
        "Searching web...",
        "Compiling results..."
      ];

      for (const step of steps) {
        setSearchState(prev => ({ ...prev, currentStep: step }));
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      const results = await mockSearch(searchQuery, uploadedImages);
      setSearchState(prev => ({
        ...prev,
        isLoading: false,
        results
      }));
    } catch (error) {
      setSearchState(prev => ({
        ...prev,
        isLoading: false,
        error: "An error occurred during the search. Please try again."
      }));
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      handleSearch();
    }
  };

  const handleFileSelect = (files: FileList) => {
    const newImages: string[] = [];
    const remainingSlots = 5 - uploadedImages.length;
    
    Array.from(files).slice(0, remainingSlots).forEach(file => {
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          newImages.push(e.target?.result as string);
          if (newImages.length === Math.min(files.length, remainingSlots)) {
            setUploadedImages(prev => [...prev, ...newImages]);
          }
        };
        reader.readAsDataURL(file);
      }
    });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (uploadedImages.length < 5) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && uploadedImages.length < 5) {
      handleFileSelect(e.target.files);
    }
  };

  const clearImage = (index: number) => {
    setUploadedImages(prev => prev.filter((_, i) => i !== index));
  };

  const clearAllImages = () => {
    setUploadedImages([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const renderSkeletonRow = () => (
    <Table.Row>
      <Table.Cell>
        <div className="flex items-center gap-2">
          <div className="h-4 w-24 bg-neutral-100 rounded animate-pulse" />
        </div>
      </Table.Cell>
      <Table.Cell>
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 bg-neutral-100 rounded-full animate-pulse" />
          <div className="h-4 w-16 bg-neutral-100 rounded animate-pulse" />
        </div>
      </Table.Cell>
      <Table.Cell>
        <div className="h-4 w-24 bg-neutral-100 rounded animate-pulse" />
      </Table.Cell>
      <Table.Cell>
        <div className="h-6 w-16 bg-neutral-100 rounded animate-pulse" />
      </Table.Cell>
    </Table.Row>
  );

  const renderSkeletonContent = () => (
    <div className="flex w-full flex-col items-start gap-4">
      <div className="flex w-full items-center justify-between">
        <div className="h-8 w-32 bg-neutral-100 rounded animate-pulse" />
        <div className="h-8 w-8 bg-neutral-100 rounded-full animate-pulse" />
      </div>
      <div className="flex w-full flex-col items-start gap-6 rounded-md border border-solid border-neutral-border bg-default-background px-6 py-6">
        <div className="flex w-full items-start gap-4">
          <div className="h-12 w-12 bg-neutral-100 rounded animate-pulse" />
          <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
            <div className="h-6 w-48 bg-neutral-100 rounded animate-pulse" />
            <div className="flex w-full flex-col items-start gap-2">
              <div className="flex w-full items-center gap-2">
                <div className="h-4 w-24 bg-neutral-100 rounded animate-pulse" />
                <div className="h-6 w-20 bg-neutral-100 rounded animate-pulse" />
              </div>
              <div className="h-4 w-full bg-neutral-100 rounded animate-pulse" />
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1">
                  <div className="h-4 w-4 bg-neutral-100 rounded animate-pulse" />
                  <div className="h-4 w-32 bg-neutral-100 rounded animate-pulse" />
                </div>
                <div className="flex items-center gap-1">
                  <div className="h-4 w-4 bg-neutral-100 rounded animate-pulse" />
                  <div className="h-4 w-24 bg-neutral-100 rounded animate-pulse" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Table
        header={
          <Table.HeaderRow>
            <Table.HeaderCell>Title</Table.HeaderCell>
            <Table.HeaderCell>Platform</Table.HeaderCell>
            <Table.HeaderCell>Time</Table.HeaderCell>
            <Table.HeaderCell>Virality Score</Table.HeaderCell>
          </Table.HeaderRow>
        }
      >
        {Array(3).fill(0).map((_, index) => renderSkeletonRow())}
      </Table>
    </div>
  );

  return (
    <DefaultPageLayout>
      <div className="flex h-full w-full flex-col items-start bg-default-background">
        <div className="flex w-full flex-col items-start gap-6 border-b border-solid border-neutral-border px-6 py-6">
          <div className="flex w-full items-center gap-2">
            <div 
              className={`flex h-auto grow shrink-0 basis-0 flex-col items-start gap-2 ${isDragging ? 'bg-brand-50' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {uploadedImages.length > 0 && (
                <div className="flex w-full flex-wrap items-start gap-2 p-2">
                  {uploadedImages.map((image, index) => (
                    <div key={index} className="relative">
                      <img 
                        src={image} 
                        alt={`Preview ${index + 1}`} 
                        className="h-12 w-12 rounded-md object-cover"
                      />
                      <IconButton
                        icon={<FeatherXCircle />}
                        onClick={() => clearImage(index)}
                        variant="neutral-tertiary"
                        size="small"
                        className="absolute -right-1 -top-1 h-4 w-4"
                      />
                    </div>
                  ))}
                  {uploadedImages.length > 0 && (
                    <IconButton
                      icon={<FeatherXCircle />}
                      onClick={clearAllImages}
                      variant="neutral-tertiary"
                      size="small"
                      className="h-4 w-4"
                    />
                  )}
                </div>
              )}
              <div className="flex w-full items-center gap-2">
                <IconButton
                  icon={<FeatherPlus />}
                  onClick={() => fileInputRef.current?.click()}
                  variant="neutral-tertiary"
                  size="small"
                  className="ml-2"
                  disabled={uploadedImages.length >= 5}
                />
                <TextField
                  className="w-full"
                  label=""
                  helpText=""
                  icon={<FeatherSearch />}
                >
                  <TextField.Input
                    placeholder={`Search for content to trace or drag & drop images (${uploadedImages.length}/5)...`}
                    value={searchQuery}
                    onChange={(event: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(event.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                  <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept="image/*"
                    multiple
                    onChange={handleFileInputChange}
                  />
                </TextField>
              </div>
            </div>
            <Button
              icon={<FeatherSearch />}
              onClick={handleSearch}
            >
              Trace
            </Button>
          </div>
          <div className="flex w-full items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge icon={<FeatherGlobe />}>All Platforms</Badge>
              <Badge variant="neutral">Last 30 days</Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="neutral-tertiary"
                size="small"
                iconRight={<FeatherChevronDown />}
                onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
              >
                Sort by: First appearance
              </Button>
            </div>
          </div>
        </div>
        <div className="flex w-full grow shrink-0 basis-0 flex-col items-start gap-8 px-6 py-6 overflow-auto">
          {searchState.isLoading ? (
            renderSkeletonContent()
          ) : (
            <div className="flex w-full flex-col items-start gap-4">
              <div className="flex w-full items-center justify-between">
                <span className="text-heading-2 font-heading-2 text-default-font">
                  Source Trace
                </span>
                <IconButton
                  icon={<FeatherShare2 />}
                  onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
                />
              </div>
              <div className="flex w-full flex-col items-start gap-6 rounded-md border border-solid border-neutral-border bg-default-background px-6 py-6">
                <div className="flex w-full items-start gap-4">
                  <Avatar
                    size="large"
                    image="https://images.unsplash.com/photo-1599305445671-ac291c95aaa9"
                    square={true}
                  >
                    A
                  </Avatar>
                  <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                    <span className="text-heading-2 font-heading-2 text-default-font mobile:h-auto mobile:w-auto mobile:flex-none">
                      Breaking: Tech Workforce Reduction
                    </span>
                    <div className="flex w-full flex-col items-start gap-2">
                      <div className="flex w-full items-center gap-2">
                        <span className="text-body-bold font-body-bold text-default-font">
                          TechCrunch
                        </span>
                        <Badge>Original Source</Badge>
                      </div>
                      <span className="text-body font-body text-default-font">
                        Breaking: Major tech companies announce significant
                        workforce reductions as AI integration accelerates
                      </span>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <FeatherClock className="text-caption font-caption text-subtext-color" />
                          <span className="text-caption font-caption text-subtext-color">
                            Jan 15, 2024 • 9:45 AM EST
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <FeatherGlobe className="text-caption font-caption text-subtext-color" />
                          <span className="text-caption font-caption text-subtext-color">
                            Emily Rodriguez
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <Table
                header={
                  <Table.HeaderRow>
                    <Table.HeaderCell>Title</Table.HeaderCell>
                    <Table.HeaderCell>Platform</Table.HeaderCell>
                    <Table.HeaderCell>Time</Table.HeaderCell>
                    <Table.HeaderCell>Virality Score</Table.HeaderCell>
                  </Table.HeaderRow>
                }
              >
                {searchState.results?.map((result, index) => (
                  <Table.Row key={index}>
                    <Table.Cell>
                      <span className="text-body-bold font-body-bold text-default-font">
                        {result.title}
                      </span>
                    </Table.Cell>
                    <Table.Cell>
                      <div className="flex items-center gap-2">
                        <Avatar
                          size="small"
                          image={result.platformIcon}
                        >
                          {result.platform.charAt(0)}
                        </Avatar>
                        <span className="text-body-bold font-body-bold text-default-font">
                          {result.platform}
                        </span>
                      </div>
                    </Table.Cell>
                    <Table.Cell>
                      <span className="text-body font-body text-default-font">
                        {result.timestamp}
                      </span>
                    </Table.Cell>
                    <Table.Cell>
                      <Badge variant={result.viralityScore === 'High' ? 'success' : result.viralityScore === 'Medium' ? 'warning' : 'neutral'}>
                        {result.viralityScore.charAt(0).toUpperCase() + result.viralityScore.slice(1)}
                      </Badge>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table>
            </div>
          )}
          <div className="flex w-full flex-col items-start gap-4">
            <div className="flex w-full items-center justify-between">
              <span className="text-heading-3 font-heading-3 text-default-font">
                Community Notes
              </span>
              <Button
                variant="brand-secondary"
                icon={<FeatherPlus />}
                onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
              >
                Add Note
              </Button>
            </div>
            <div className="flex w-full flex-col items-start gap-4">
              <div className="flex w-full items-start gap-4 rounded-md border border-solid border-neutral-border bg-default-background px-4 py-4">
                <Avatar image="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde">
                  J
                </Avatar>
                <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-body-bold font-body-bold text-default-font">
                      John Smith
                    </span>
                    <Badge>Fact Checker</Badge>
                  </div>
                  <span className="text-body font-body text-default-font">
                    Original source verified through archived timestamps and
                    digital signatures. Content appears to be authentic based on
                    multiple verification methods.
                  </span>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="neutral-tertiary"
                      size="small"
                      icon={<FeatherThumbsUp />}
                      onClick={(
                        event: React.MouseEvent<HTMLButtonElement>
                      ) => {}}
                    >
                      Helpful (24)
                    </Button>
                    <Button
                      variant="neutral-tertiary"
                      size="small"
                      onClick={(
                        event: React.MouseEvent<HTMLButtonElement>
                      ) => {}}
                    >
                      Reply
                    </Button>
                  </div>
                </div>
              </div>
              <div className="flex w-full items-start gap-4 rounded-md border border-solid border-neutral-border bg-default-background px-4 py-4">
                <Avatar image="https://images.unsplash.com/photo-1494790108377-be9c29b29330">
                  A
                </Avatar>
                <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-body-bold font-body-bold text-default-font">
                      Alice Chen
                    </span>
                    <Badge variant="warning">Researcher</Badge>
                  </div>
                  <span className="text-body font-body text-default-font">
                    Additional context: Similar claims appeared in private
                    forums 24 hours before the viral spread, but couldn&#39;t be
                    independently verified.
                  </span>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="neutral-tertiary"
                      size="small"
                      icon={<FeatherThumbsUp />}
                      onClick={(
                        event: React.MouseEvent<HTMLButtonElement>
                      ) => {}}
                    >
                      Helpful (18)
                    </Button>
                    <Button
                      variant="neutral-tertiary"
                      size="small"
                      onClick={(
                        event: React.MouseEvent<HTMLButtonElement>
                      ) => {}}
                    >
                      Reply
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading Modal */}
        {searchState.isLoading && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <div className="flex items-center gap-3 mb-4">
                <FeatherLoader className="animate-spin text-brand-600" />
                <span className="text-body font-body text-default-font">
                  {searchState.currentStep}
                </span>
              </div>
              <div className="w-full bg-neutral-100 rounded-full h-2">
                <div 
                  className="bg-brand-600 h-2 rounded-full transition-all duration-1000"
                  style={{ 
                    width: searchState.currentStep === "Analyzing input..." ? "33%" :
                           searchState.currentStep === "Searching web..." ? "66%" : "100%"
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {searchState.error && (
          <div className="w-full px-6 py-3 bg-error-50 text-error-700">
            {searchState.error}
          </div>
        )}
      </div>
    </DefaultPageLayout>
  );
}

export default SourceTrace; 