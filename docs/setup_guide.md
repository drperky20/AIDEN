# AIDEN V2 Setup Guide

This guide will walk you through setting up AIDEN V2 on your system.

## Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm (for frontend)
- Git
- Google API Key for Gemini models

## Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AIDEN.git
cd AIDEN
```

### 2. Create a Python Virtual Environment

```bash
# Using venv
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env  # If .env.example exists
```

Edit the `.env` file and set your Google API Key:

```
GOOGLE_API_KEY=your_google_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
ENVIRONMENT=development
```

You can get a Google API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Start the Backend Server

```bash
./scripts/run_dev.sh
```

The backend API will be available at `http://localhost:8000`.

## Frontend Setup (Optional)

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Start the Frontend Development Server

```bash
npm run dev
```

Or use the script:

```bash
./scripts/run_dev.sh frontend
```

The frontend will be available at `http://localhost:3000`.

## Testing the Installation

### API Documentation

Visit `http://localhost:8000/docs` to see the Swagger UI documentation for the API.

### Health Check

```bash
curl http://localhost:8000/health
```

Should return a JSON response with the status of various components.

### Chat API

You can test the chat API with:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello AIDEN!", "session_id": "test"}'
```

## Troubleshooting

### API Key Issues

If you see errors about invalid API keys:

1. Make sure your Google API Key is correctly set in the `.env` file
2. Verify that your API key has access to the Gemini models
3. Check for any rate limiting or quota issues

### Database Errors

If you encounter database errors:

1. Make sure the `data` directory exists and is writable
2. Check the logs for specific error messages
3. Try deleting the database file and restarting (this will lose conversation history)

### Import Errors

If you see Python import errors:

1. Make sure you're in the activated virtual environment
2. Verify that all dependencies are installed
3. Check that you're running the commands from the correct directory

## Next Steps

- Explore adding custom tools in the `backend/tools` directory
- Check out the Agno documentation for more advanced agent features
- Look into integrating with Mem0 for enhanced memory capabilities 