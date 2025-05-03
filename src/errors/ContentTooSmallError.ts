export class ContentTooSmallError extends Error {
  constructor(message: string = 'Content is too small to be processed') {
    super(message);
    this.name = 'ContentTooSmallError';
  }
} 