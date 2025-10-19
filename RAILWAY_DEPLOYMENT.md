# Railway Deployment Guide for TrinityAI

## Prerequisites

1. A Railway account
2. Your API keys for OpenAI, Gemini, and Claude
3. A MongoDB database (can use Railway's MongoDB service)

## Deployment Steps

### 1. Connect Your Repository

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your TrinityAI repository

### 2. Set Environment Variables

In Railway dashboard, go to your project settings and add these environment variables:

```
OPENAI_KEY=your_openai_api_key_here
GEMINI_KEY=your_gemini_api_key_here
CLAUDE_KEY=your_claude_api_key_here
MONGODB_URI=your_mongodb_connection_string_here
```

### 3. Deploy

Railway will automatically:

- Build the Docker image using the Dockerfile
- Deploy the application
- Set up health checks

## What Was Fixed

### Docker Issues

- ✅ Removed model download during build (moved to runtime)
- ✅ Added proper error handling
- ✅ Created `.dockerignore` to exclude unnecessary files
- ✅ Added non-root user for security
- ✅ Used Railway's PORT environment variable

### Application Issues

- ✅ Fixed critical bug in `getWeights()` function (was returning None)
- ✅ Added proper error handling for missing API keys
- ✅ Added graceful fallback for MongoDB connection failures
- ✅ Added health check endpoint
- ✅ Created production WSGI configuration

### Railway Configuration

- ✅ Added `railway.json` with proper build and deploy settings
- ✅ Configured health checks
- ✅ Set up proper restart policies

## Environment Variables Required

| Variable      | Description                  | Required      |
| ------------- | ---------------------------- | ------------- |
| `OPENAI_KEY`  | OpenAI API key               | Yes           |
| `GEMINI_KEY`  | Google Gemini API key        | Yes           |
| `CLAUDE_KEY`  | Anthropic Claude API key     | Yes           |
| `MONGODB_URI` | MongoDB connection string    | No (optional) |
| `PORT`        | Port number (set by Railway) | Auto          |

## Health Check

The application includes a health check endpoint at `/health` that returns:

```json
{ "status": "healthy", "message": "TrinityAI is running" }
```

## Troubleshooting

### Build Failures

- Check that all environment variables are set
- Verify Docker build logs in Railway dashboard

### Runtime Errors

- Check application logs in Railway dashboard
- Verify API keys are correct
- Ensure MongoDB URI is valid (if using database features)

### Performance

- The app uses 2 Gunicorn workers by default
- Timeout is set to 120 seconds for AI API calls
- Model loading happens at runtime (not during build)
