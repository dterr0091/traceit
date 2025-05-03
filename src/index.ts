import express, { Request, Response } from 'express';
import { runCLI } from './cli';

const app = express();
const port = process.env.PORT || 3000;

// Basic health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

// CLI endpoint
app.post('/trace', async (_req: Request, res: Response) => {
  try {
    const result = await runCLI();
    res.json(result);
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    res.status(500).json({ error: errorMessage });
  }
});

// Start the server
if (process.env.NODE_ENV !== 'test') {
  app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
  });
}

export default app; 