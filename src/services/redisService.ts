import { createClient } from 'redis';
import { Thought } from '../types/thoughts';

export class RedisService {
  private client;
  private isConnected = false;

  constructor() {
    this.client = createClient({
      url: process.env.REDIS_URL || 'redis://localhost:6379'
    });

    this.client.on('error', (err) => {
      console.error('Redis Client Error', err);
    });
  }

  async connect() {
    if (!this.isConnected) {
      await this.client.connect();
      this.isConnected = true;
    }
  }

  async disconnect() {
    if (this.isConnected) {
      await this.client.disconnect();
      this.isConnected = false;
    }
  }

  async storeThought(id: string, thought: Thought): Promise<void> {
    await this.connect();
    await this.client.set(`thought:${id}`, JSON.stringify(thought));
  }

  async storeSecondaryThoughts(primaryId: string, thoughts: Thought[]): Promise<void> {
    await this.connect();
    
    // Store each thought individually
    for (let i = 0; i < thoughts.length; i++) {
      const thoughtId = `${primaryId}:secondary:${i}`;
      await this.client.set(`thought:${thoughtId}`, JSON.stringify(thoughts[i]));
    }
    
    // Store the list of secondary thought IDs
    const secondaryIds = thoughts.map((_, i) => `${primaryId}:secondary:${i}`);
    await this.client.set(`thought:${primaryId}:secondaries`, JSON.stringify(secondaryIds));
  }

  async getThought(id: string): Promise<Thought | null> {
    await this.connect();
    const thought = await this.client.get(`thought:${id}`);
    
    if (!thought) return null;
    return JSON.parse(thought);
  }

  async getSecondaryThoughtIds(primaryId: string): Promise<string[]> {
    await this.connect();
    const ids = await this.client.get(`thought:${primaryId}:secondaries`);
    
    if (!ids) return [];
    return JSON.parse(ids);
  }

  async getSecondaryThoughts(primaryId: string): Promise<Thought[]> {
    const secondaryIds = await this.getSecondaryThoughtIds(primaryId);
    const thoughts: Thought[] = [];
    
    for (const id of secondaryIds) {
      const thought = await this.getThought(id);
      if (thought) {
        thoughts.push(thought);
      }
    }
    
    return thoughts;
  }
} 