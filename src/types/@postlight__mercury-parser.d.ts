declare module '@postlight/mercury-parser' {
  export interface ParseResult {
    title?: string;
    author?: string;
    date_published?: string;
    content?: string;
    lead_image_url?: string;
  }

  export function parse(url: string, options?: { html?: string }): Promise<ParseResult>;
} 