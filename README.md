# TrinityAI - Simplified

A minimal AI chat application that combines OpenAI, Google Gemini, and Anthropic Claude responses.

## Features

- Simple web interface
- Three AI service endpoints: `/openai`, `/gemini`, `/claude`
- Health check endpoint: `/health`
- Railway deployment ready

## Environment Variables

Set these in Railway dashboard:

- `OPENAI_KEY` - Your OpenAI API key
- `GEMINI_KEY` - Your Google Gemini API key
- `CLAUDE_KEY` - Your Anthropic Claude API key

## Deployment

1. Push to GitHub
2. Connect to Railway
3. Set environment variables
4. Deploy

That's it! No complex configuration needed.
