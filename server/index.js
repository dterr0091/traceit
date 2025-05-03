const express = require('express');
const cors = require('cors');
const OpenAI = require('openai');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// OpenAI analysis endpoint
app.post('/api/analyze', async (req, res) => {
  try {
    const { post } = req.body;

    const response = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        {
          role: 'system',
          content: 'You are an expert content analyst. Analyze the provided content and generate search queries to find the original source and related content. Focus on identifying key topics and suggesting a relevant timeframe for the search.'
        },
        {
          role: 'user',
          content: buildTextPrompt(post)
        }
      ],
      temperature: 0.7,
      max_tokens: 1000
    });

    const content = response.choices[0]?.message?.content;
    if (!content) {
      throw new Error('Empty response from OpenAI');
    }

    const result = JSON.parse(content);
    validateAnalysisResult(result);
    
    res.json(result);
  } catch (error) {
    console.error('Error in OpenAI analysis:', error);
    res.status(500).json({ error: 'Failed to analyze content' });
  }
});

function buildTextPrompt(post) {
  return `
    Analyze the following content and generate search queries to find its original source and related content:

    Title: ${post.title}
    Content: ${post.content}
    Publication Date: ${post.date_published}
    Platform: ${post.platform}

    Please provide:
    1. Three search queries optimized for finding the original source and related content
    2. Key topics identified in the content
    3. A suggested timeframe for the search (e.g., "2020-2023")

    Format your response as a JSON object with the following structure:
    {
      "searchQueries": ["query1", "query2", "query3"],
      "keyTopics": ["topic1", "topic2"],
      "suggestedTimeframe": "YYYY-YYYY"
    }
  `;
}

function validateAnalysisResult(result) {
  if (!result.searchQueries || !Array.isArray(result.searchQueries) || result.searchQueries.length === 0) {
    throw new Error('Invalid search queries in analysis result');
  }
  if (!result.keyTopics || !Array.isArray(result.keyTopics) || result.keyTopics.length === 0) {
    throw new Error('Invalid key topics in analysis result');
  }
  if (!result.suggestedTimeframe || typeof result.suggestedTimeframe !== 'string') {
    throw new Error('Invalid suggested timeframe in analysis result');
  }
}

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
}); 