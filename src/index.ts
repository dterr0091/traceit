import express, { Request, Response } from 'express';
import { runCLI } from './cli';

const app = express();
const port = process.env.PORT || 3000;

// Add JSON body parsing middleware
app.use(express.json());

// Basic health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  console.log('Health check endpoint called');
  res.json({ status: 'ok' });
});

// CLI endpoint
app.post('/trace', async (_req: Request, res: Response) => {
  console.log('Trace endpoint called');
  try {
    const result = await runCLI();
    console.log('CLI execution completed:', result);
    res.json(result);
  } catch (error: unknown) {
    console.error('Error in trace endpoint:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    res.status(500).json({ error: errorMessage });
  }
});

// Error handling middleware
app.use((err: Error, _req: Request, res: Response, _next: Function) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: err.message });
});

// Start the server
if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
  });
}

export default app; 