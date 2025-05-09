"use client";

import React, { useState, useRef } from "react";
import { DefaultPageLayout } from "@/ui/layouts/DefaultPageLayout";
import { TextField } from "@/ui/components/TextField";
import { FeatherSearch } from "@subframe/core";
import { FeatherXCircle } from "@subframe/core";
import { Button } from "@/ui/components/Button";
import { Badge } from "@/ui/components/Badge";
import { FeatherGlobe } from "@subframe/core";
import { IconButton } from "@/ui/components/IconButton";
import { FeatherShare2 } from "@subframe/core";
import { Avatar } from "@/ui/components/Avatar";
import { FeatherClock } from "@subframe/core";
import { Table } from "@/ui/components/Table";
import { FeatherPlus } from "@subframe/core";
import { FeatherThumbsUp } from "@subframe/core";
import { FeatherLoader } from "@subframe/core";
import { FeatherUpload } from "@subframe/core";
import { mockCommunityNotes } from '../services/mockData';
import { SearchState, CommunityNote, SearchInput } from '../types/sourceTrace';
import { SearchService } from '../services';
import { ShareModal } from "@/ui/components/ShareModal";

function SourceTrace() {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [uploadedImages, setUploadedImages] = useState<string[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [showRequestTextArea, setShowRequestTextArea] = useState(false);
  const [requestText, setRequestText] = useState("");
  const [deleteModalState, setDeleteModalState] = useState<{ isOpen: boolean; noteId: number | null }>({
    isOpen: false,
    noteId: null
  });
  const [searchState, setSearchState] = useState<SearchState>({
    isLoading: false,
    currentStep: '',
    error: null,
    results: null
  });
  const [communityNotes, setCommunityNotes] = useState<CommunityNote[]>(mockCommunityNotes);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const searchService = useRef<SearchService>(new SearchService());
  const [showShareModal, setShowShareModal] = useState(false);

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
      // Prepare search input
      const searchInput: SearchInput = {
        query: searchQuery,
        images: []
      };

      // Perform search
      const results = await searchService.current.search(searchInput.query ?? '');
      
      // Transform results into the expected format
      const originalSources = results.filter(result => result.isOriginalSource);
      const viralPoints = results.filter(result => !result.isOriginalSource);

      const viralResults = viralPoints.map(result => ({
        title: result.title,
        platform: result.platform,
        timestamp: result.timestamp,
        viralityScore: result.viralityScore,
        platformIcon: result.platformIcon,
        isOriginalSource: false
      }));

      // Update community notes based on search results
      const updatedNotes = mockCommunityNotes.map(note => ({
        ...note,
        content: note.content.replace(
          "Original source verified",
          `Original source verified for "${originalSources[0]?.title || 'the search query'}"`
        )
      }));
      setCommunityNotes(updatedNotes);

      setSearchState(prev => ({
        ...prev,
        isLoading: false,
        results: viralResults,
        currentStep: 'completed',
        error: null
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

  const handleShareClick = () => {
    setShowShareModal(true);
  };

  const handleSubmitRequest = () => {
    if (!requestText.trim()) return;
    
    const newNote: CommunityNote = {
      id: Date.now(), // Using timestamp as number ID
      user: {
        name: "You",
        avatar: "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9",
        badge: "Contributor"
      },
      content: requestText,
      helpfulCount: 0,
      timestamp: new Date().toLocaleString('en-US', {
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    };

    setCommunityNotes(prevNotes => [newNote, ...prevNotes]);
    setShowRequestTextArea(false);
    setRequestText("");
  };

  const handleDeleteNote = (noteId: number) => {
    setDeleteModalState({ isOpen: true, noteId });
  };

  const handleHelpfulClick = (noteId: number) => {
    setCommunityNotes(prevNotes => 
      prevNotes.map(note => 
        note.id === noteId 
          ? { ...note, helpfulCount: note.helpfulCount + 1 }
          : note
      )
    );
  };

  const confirmDelete = () => {
    if (deleteModalState.noteId) {
      setCommunityNotes(prevNotes => prevNotes.filter(note => note.id !== deleteModalState.noteId));
      setDeleteModalState({ isOpen: false, noteId: null });
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
        <span className="text-heading-2 font-heading-2 text-default-font">
          Source Trace
        </span>
        <IconButton
          icon={<FeatherShare2 />}
          onClick={() => {}}
        />
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
        {Array(3).fill(0).map((_, index) => (
          <React.Fragment key={`skeleton-${index}`}>
            {renderSkeletonRow()}
          </React.Fragment>
        ))}
      </Table>
    </div>
  );

  const renderEmptyState = () => (
    <div className="flex w-full flex-col items-center gap-6 py-12">
      <div className="flex flex-col items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-50">
          <FeatherSearch className="text-brand-600" />
        </div>
        <div className="flex flex-col items-center gap-2">
          <span className="text-heading-2 font-heading-2 text-default-font">
            Start Tracing Sources
          </span>
          <span className="text-body font-body text-subtext-color text-center max-w-md">
            Enter a search query or upload images to trace the origin and spread of content across different platforms.
          </span>
        </div>
      </div>
      <div className="flex flex-col items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100">
            <FeatherSearch className="text-neutral-600" />
          </div>
          <span className="text-body font-body text-default-font">
            Search by keywords or phrases
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100">
            <FeatherUpload className="text-neutral-600" />
          </div>
          <span className="text-body font-body text-default-font">
            Upload up to 5 images to trace
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-neutral-100">
            <FeatherGlobe className="text-neutral-600" />
          </div>
          <span className="text-body font-body text-default-font">
            View results across multiple platforms
          </span>
        </div>
      </div>
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
        </div>
        <div className="flex w-full grow shrink-0 basis-0 flex-col items-start gap-8 px-6 py-6 overflow-auto">
          {searchState.isLoading ? (
            renderSkeletonContent()
          ) : searchState.results ? (
            <div className="flex w-full flex-col items-start gap-4">
              <div className="flex w-full items-center justify-between">
                <span className="text-heading-2 font-heading-2 text-default-font">
                  Source Trace
                </span>
                <IconButton
                  icon={<FeatherShare2 />}
                  onClick={handleShareClick}
                />
              </div>
              <div className="flex w-full flex-col items-start gap-6 rounded-md border border-solid border-neutral-border bg-default-background px-6 py-6">
                <div className="flex w-full items-start gap-4">
                  <Avatar
                    size="large"
                    image={searchState.results?.[0]?.platformIcon || "https://images.unsplash.com/photo-1599305445671-ac291c95aaa9"}
                    square={true}
                  >
                    {searchState.results?.[0]?.platform.charAt(0) || "A"}
                  </Avatar>
                  <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                    <span className="text-heading-2 font-heading-2 text-default-font mobile:h-auto mobile:w-auto mobile:flex-none">
                      {searchState.results?.[0]?.title || "Breaking: Tech Workforce Reduction"}
                    </span>
                    <div className="flex w-full flex-col items-start gap-2">
                      <div className="flex w-full items-center gap-2">
                        <span className="text-body-bold font-body-bold text-default-font">
                          {searchState.results?.[0]?.platform || "TechCrunch"}
                        </span>
                        <Badge>Original Source</Badge>
                      </div>
                      <span className="text-body font-body text-default-font">
                        {searchState.results?.[0]?.title 
                          ? `Breaking: ${searchState.results[0].title} - Analysis and impact on the tech industry`
                          : "Breaking: Major tech companies announce significant workforce reductions as AI integration accelerates"}
                      </span>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1">
                          <FeatherClock className="text-caption font-caption text-subtext-color" />
                          <span className="text-caption font-caption text-subtext-color">
                            {searchState.results?.[0]?.timestamp || "Jan 15, 2024 • 9:45 AM EST"}
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
              <div className="flex w-full flex-col items-start gap-4">
                <div className="flex w-full items-center justify-between">
                  <span className="text-heading-3 font-heading-3 text-default-font">
                    Virality
                  </span>
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
                    <Table.Row key={`result-${result.title}-${index}`}>
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
                          {result.viralityScore}
                        </Badge>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table>
              </div>
              <div className="flex w-full flex-col items-start gap-4">
                <div className="flex w-full items-center justify-between">
                  <span className="text-heading-3 font-heading-3 text-default-font">
                    Change Requests
                  </span>
                  <Button
                    variant="brand-secondary"
                    icon={<FeatherPlus />}
                    onClick={() => setShowRequestTextArea(!showRequestTextArea)}
                  >
                    Add Request
                  </Button>
                </div>
                <div className="flex w-full flex-col items-start gap-4">
                  {showRequestTextArea && (
                    <div className="flex w-full items-start gap-4 rounded-md border border-solid border-neutral-border bg-default-background px-4 py-4">
                      <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                        <textarea
                          className="w-full h-32 p-2 rounded-md border border-solid border-neutral-border text-body font-body text-default-font"
                          placeholder="Enter your change request here..."
                          value={requestText}
                          onChange={(e) => setRequestText(e.target.value)}
                        />
                        <div className="flex items-center gap-2">
                          <Button
                            variant="brand-secondary"
                            size="small"
                            onClick={handleSubmitRequest}
                          >
                            Submit
                          </Button>
                          <Button
                            variant="neutral-tertiary"
                            size="small"
                            onClick={() => {
                              setShowRequestTextArea(false);
                              setRequestText("");
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                  {communityNotes.map((note) => (
                    <div key={note.id} className="flex w-full items-start gap-4 rounded-md border border-solid border-neutral-border bg-default-background px-4 py-4">
                      <Avatar image={note.user.avatar}>
                        {note.user.name.charAt(0)}
                      </Avatar>
                      <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-body-bold font-body-bold text-default-font">
                            {note.user.name}
                          </span>
                          <Badge variant={note.user.badge === "Fact Checker" ? "success" : "warning"}>
                            {note.user.badge}
                          </Badge>
                        </div>
                        <span className="text-body font-body text-default-font">
                          {note.content}
                        </span>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="neutral-tertiary"
                            size="small"
                            icon={<FeatherThumbsUp />}
                            onClick={() => handleHelpfulClick(note.id)}
                          >
                            Helpful ({note.helpfulCount})
                          </Button>
                          <Button
                            variant="neutral-tertiary"
                            size="small"
                            onClick={() => {}}
                          >
                            Reply
                          </Button>
                          {note.user.name === "You" && (
                            <Button
                              variant="destructive-primary"
                              size="small"
                              onClick={() => handleDeleteNote(note.id)}
                            >
                              Delete
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            renderEmptyState()
          )}
        </div>

        {/* Delete Confirmation Modal */}
        {deleteModalState.isOpen && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <div className="flex flex-col items-start gap-4">
                <span className="text-heading-3 font-heading-3 text-default-font">
                  Are you sure?
                </span>
                <span className="text-body font-body text-default-font">
                  This cannot be undone.
                </span>
                <div className="flex items-center gap-2 w-full justify-end">
                  <Button
                    variant="neutral-tertiary"
                    size="small"
                    onClick={() => setDeleteModalState({ isOpen: false, noteId: null })}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive-primary"
                    size="small"
                    onClick={confirmDelete}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

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
      {showShareModal && searchState.results && (
        <ShareModal
          originalSource={searchState.results[0]}
          viralPoints={searchState.results.slice(1, 4)}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </DefaultPageLayout>
  );
}

export default SourceTrace; 