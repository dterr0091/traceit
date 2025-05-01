import React from 'react';
import { Select } from '@/ui/components/Select';

export interface SearchFiltersProps {
  onPlatformChange: (platform: string) => void;
  onTimeRangeChange: (timeRange: string) => void;
  onSortChange: (sortBy: string) => void;
}

const platforms = [
  { value: 'all', label: 'All Platforms' },
  { value: 'twitter', label: 'Twitter' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'instagram', label: 'Instagram' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'news', label: 'News Sites' },
];

const timeRanges = [
  { value: 'all', label: 'All Time' },
  { value: '5y', label: '5 Years' },
  { value: '1y', label: '1 Year' },
  { value: '6m', label: '6 Months' },
  { value: '3m', label: '3 Months' },
  { value: '1m', label: '1 Month' },
  { value: '1w', label: '1 Week' },
];

const sortOptions = [
  { value: 'first_appearance', label: 'First Appearance' },
  { value: 'most_viral', label: 'Most Viral' },
];

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  onPlatformChange,
  onTimeRangeChange,
  onSortChange,
}) => {
  return (
    <div className="flex items-center gap-4">
      <Select.Root 
        defaultValue="all" 
        onValueChange={onPlatformChange}
        placeholder="All Platforms"
      >
        <Select.Trigger className="h-10 w-40 rounded-md border border-solid border-neutral-border bg-white">
          <Select.TriggerValue />
        </Select.Trigger>
        <Select.Content>
          {platforms.map((platform) => (
            <Select.Item key={platform.value} value={platform.value}>
              {platform.label}
            </Select.Item>
          ))}
        </Select.Content>
      </Select.Root>

      <Select.Root 
        defaultValue="all" 
        onValueChange={onTimeRangeChange}
        placeholder="All Time"
      >
        <Select.Trigger className="h-10 w-32 rounded-md border border-solid border-neutral-border bg-white">
          <Select.TriggerValue />
        </Select.Trigger>
        <Select.Content>
          {timeRanges.map((timeRange) => (
            <Select.Item key={timeRange.value} value={timeRange.value}>
              {timeRange.label}
            </Select.Item>
          ))}
        </Select.Content>
      </Select.Root>

      <Select.Root 
        defaultValue="first_appearance" 
        onValueChange={onSortChange}
        placeholder="Sort by"
      >
        <Select.Trigger className="h-10 w-40 rounded-md border border-solid border-neutral-border bg-white">
          <Select.TriggerValue />
        </Select.Trigger>
        <Select.Content>
          {sortOptions.map((option) => (
            <Select.Item key={option.value} value={option.value}>
              {option.label}
            </Select.Item>
          ))}
        </Select.Content>
      </Select.Root>
    </div>
  );
}; 