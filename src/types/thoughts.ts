import { PerplexitySearchResult } from './sourceTrace';

export interface Thought {
  id: string;
  content: string;
  embedding: number[];
  score?: number;
}

export interface PrimaryThought extends Thought {
  origin: string;
  viral: boolean;
  evidence: PerplexitySearchResult[];
}

export interface ThoughtLineage {
  primaryThought: PrimaryThought;
  secondaryCount: number;
}

export interface QuotaStatus {
  remaining: number;
  limit: number;
  reset: Date;
} 