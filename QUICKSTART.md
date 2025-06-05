# Quick Start Guide

Get your Agno Gemini Agent running in 3 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Google API Key
- Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- Create a new API key
- Copy it for the next step

### 3. Set Your API Key

**Option A: Environment Variable (Recommended)**
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Option B: Create .env file**
```bash
cp .env.example .env
# Edit .env file and add your API key
# (the .env file is ignored by Git)
```

### 4. Test the Agent

**Option A: Simple Test (Recommended first)**
```bash
python3 simple_test.py
```

**Option B: Full Test with Web Search**
```bash
python3 test_agent.py
```

### 5. Start the Web UI
```bash
python3 run.py
```

Open http://localhost:8000 in your browser and start chatting!

## 🎯 What You Get

- **Smart AI Agent**: Powered by Gemini 2.5 Flash Preview
- **Web Search**: Can search the internet for current information
- **Beautiful UI**: Modern, responsive chat interface
- **Ready to Use**: No complex configuration needed

## 💬 Try These Examples

- "What's the latest news about AI?"
- "Explain quantum computing"
- "Write a Python function to calculate fibonacci numbers"
- "What's the weather like today?"

## 🔧 Need Help?

Check the full [README.md](README.md) for detailed instructions and troubleshooting. 