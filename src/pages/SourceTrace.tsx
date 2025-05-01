"use client";

import React, { useState } from "react";
import { DefaultPageLayout } from "@/ui/layouts/DefaultPageLayout";
import { TextField } from "@/ui/components/TextField";
import { FeatherSearch, FeatherXCircle, FeatherShare2, FeatherClock, FeatherGlobe, FeatherPlus, FeatherThumbsUp } from "@subframe/core";
import { Button } from "@/ui/components/Button";
import { Badge } from "@/ui/components/Badge";
import { IconButton } from "@/ui/components/IconButton";
import { Avatar } from "@/ui/components/Avatar";
import { Table } from "@/ui/components/Table";
import { SearchFilters } from "@/components/SearchFilters";

function SourceTrace() {
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [selectedPlatform, setSelectedPlatform] = useState("all");
  const [selectedTimeRange, setSelectedTimeRange] = useState("all");
  const [selectedSort, setSelectedSort] = useState("first_appearance");

  const handleSearch = async () => {
    setIsLoading(true);
    // Simulate API call with filters
    setTimeout(() => {
      setSearchResults([
        {
          id: 1,
          title: "Breaking: Major tech companies announce significant workforce reductions",
          source: "TechCrunch",
          date: "Jan 15, 2024 • 9:45 AM EST",
          url: "techcrunch.com",
          isVerified: true
        },
        {
          id: 2,
          title: "AI Integration Leads to Job Cuts in Tech Sector",
          source: "The Verge",
          date: "Jan 15, 2024 • 10:30 AM EST",
          url: "theverge.com",
          isVerified: false
        }
      ]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <DefaultPageLayout>
      <div className="flex h-full w-full flex-col items-start bg-default-background">
        <div className="flex w-full flex-col items-start gap-6 border-b border-solid border-neutral-border px-6 py-6">
          <div className="flex w-full max-w-[1440px] mx-auto flex-col items-start gap-6">
            <div className="flex w-full items-center gap-2">
              <TextField
                className="h-auto grow shrink-0 basis-0"
                label=""
                helpText=""
                icon={<FeatherSearch />}
                iconRight={<FeatherXCircle />}
              >
                <TextField.Input
                  placeholder="Search for content to trace..."
                  value={searchQuery}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                    setSearchQuery(event.target.value);
                  }}
                />
              </TextField>
              <Button
                icon={<FeatherSearch />}
                onClick={handleSearch}
              >
                Trace
              </Button>
            </div>
            <SearchFilters
              onPlatformChange={setSelectedPlatform}
              onTimeRangeChange={setSelectedTimeRange}
              onSortChange={setSelectedSort}
            />
          </div>
        </div>
        <div className="flex w-full grow shrink-0 basis-0 flex-col items-start gap-8 px-6 py-6 overflow-auto">
          <div className="flex w-full max-w-[1440px] mx-auto flex-col items-start gap-4">
            <div className="flex w-full items-center justify-between">
              <span className="text-heading-2 font-heading-2 text-default-font">
                Source Trace
              </span>
              <IconButton
                icon={<FeatherShare2 />}
                onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
              />
            </div>
            {isLoading ? (
              <LoadingSkeleton />
            ) : searchResults.length > 0 ? (
              searchResults.map((result) => (
                <div key={result.id} className="flex w-full flex-col items-start gap-6 rounded-md border border-solid border-neutral-border bg-default-background px-6 py-6">
                  <div className="flex w-full items-start gap-4">
                    <Avatar
                      size="large"
                      image="https://images.unsplash.com/photo-1599305445671-ac291c95aaa9"
                      square={true}
                    >
                      {result.source.charAt(0)}
                    </Avatar>
                    <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
                      <span className="text-heading-2 font-heading-2 text-default-font">
                        {result.title}
                      </span>
                      <div className="flex w-full flex-col items-start gap-2">
                        <div className="flex w-full items-center gap-2">
                          <span className="text-body-bold font-body-bold text-default-font">
                            {result.source}
                          </span>
                          {result.isVerified && <Badge>Verified Source</Badge>}
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-1">
                            <FeatherClock className="text-caption font-caption text-subtext-color" />
                            <span className="text-caption font-caption text-subtext-color">
                              {result.date}
                            </span>
                          </div>
                          <div className="flex items-center gap-1">
                            <FeatherGlobe className="text-caption font-caption text-subtext-color" />
                            <span className="text-caption font-caption text-subtext-color">
                              {result.url}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex w-full flex-col items-start gap-6 rounded-md border border-solid border-neutral-border bg-default-background px-6 py-6">
                <span className="text-body font-body text-default-font">
                  No results found. Try searching for content to trace.
                </span>
              </div>
            )}
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
              <Table.Row>
                <Table.Cell>
                  <span className="text-body font-body text-default-font">
                    Breaking: Major tech companies announce layoffs
                  </span>
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-2">
                    <Avatar
                      size="small"
                      image="https://images.unsplash.com/photo-1611162617474-5b21e879e113"
                    >
                      X
                    </Avatar>
                    <span className="text-body-bold font-body-bold text-default-font">
                      Twitter
                    </span>
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <span className="text-body font-body text-default-font">
                    March 15, 9:00 AM
                  </span>
                </Table.Cell>
                <Table.Cell>
                  <Badge variant="success">High</Badge>
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>
                  <span className="text-body font-body text-default-font">
                    Tech Industry Layoffs: An Analysis
                  </span>
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-2">
                    <Avatar
                      size="small"
                      image="https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0"
                    >
                      R
                    </Avatar>
                    <span className="text-body-bold font-body-bold text-default-font">
                      Reddit
                    </span>
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <span className="text-body font-body text-default-font">
                    March 15, 10:30 AM
                  </span>
                </Table.Cell>
                <Table.Cell>
                  <Badge variant="warning">Medium</Badge>
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>
                  <span className="text-body font-body text-default-font">
                    Impact of Recent Tech Layoffs on Industry
                  </span>
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-2">
                    <Avatar
                      size="small"
                      image="https://images.unsplash.com/photo-1611162618071-b39a2ec055fb"
                    >
                      F
                    </Avatar>
                    <span className="text-body-bold font-body-bold text-default-font">
                      Facebook
                    </span>
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <span className="text-body font-body text-default-font">
                    March 15, 2:15 PM
                  </span>
                </Table.Cell>
                <Table.Cell>
                  <Badge variant="neutral">Low</Badge>
                </Table.Cell>
              </Table.Row>
            </Table>
          </div>
          <div className="flex w-full max-w-[1440px] mx-auto flex-col items-start gap-4">
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
                      onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
                    >
                      Helpful (24)
                    </Button>
                    <Button
                      variant="neutral-tertiary"
                      size="small"
                      onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
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
                      onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
                    >
                      Helpful (18)
                    </Button>
                    <Button
                      variant="neutral-tertiary"
                      size="small"
                      onClick={(event: React.MouseEvent<HTMLButtonElement>) => {}}
                    >
                      Reply
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DefaultPageLayout>
  );
}

const LoadingSkeleton = () => (
  <div className="flex w-full flex-col items-start gap-6 rounded-md border border-solid border-neutral-border bg-default-background px-6 py-6">
    <div className="flex w-full items-start gap-4">
      <div className="h-12 w-12 rounded-md bg-neutral-200 animate-pulse" />
      <div className="flex grow shrink-0 basis-0 flex-col items-start gap-2">
        <div className="h-6 w-48 bg-neutral-200 rounded animate-pulse" />
        <div className="h-4 w-full bg-neutral-200 rounded animate-pulse" />
        <div className="h-4 w-64 bg-neutral-200 rounded animate-pulse" />
      </div>
    </div>
  </div>
);

export default SourceTrace; 