# Agno Gemini Agent

A production-ready, full-stack chat application powered by Google's Gemini 2.5 Flash Preview with web search capabilities. Features a modern React frontend and optimized FastAPI backend.

## ✨ Features

- 🤖 **Gemini 2.5 Flash Preview**: Latest Google AI model with advanced capabilities
- 🔍 **Web Search**: Built-in DuckDuckGo search for current information
- 💬 **Modern React UI**: Beautiful, responsive chat interface with TypeScript
- ⚡ **High Performance**: Optimized FastAPI backend with async processing
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🛠️ **Developer Experience**: Hot reload, error handling, and comprehensive logging
- 🔧 **Easy Setup**: Automated scripts for installation, running, and cleanup

## 🏗️ Architecture

```
AIDEN/
├── backend/           # FastAPI server + Agno agent
│   ├── app.py        # Main FastAPI application
│   ├── agent.py      # Agno agent configuration
│   ├── config.py     # Configuration management
│   └── requirements.txt
├── frontend/         # React + TypeScript UI
│   ├── src/
│   │   ├── App.tsx   # Main chat component
│   │   ├── config.ts # Frontend configuration
│   │   └── ...
│   └── package.json
├── scripts/          # Automation scripts
│   ├── install.sh    # Install dependencies
│   ├── run.sh        # Start both frontend & backend
│   └── uninstall.sh  # Clean up project
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ and pip
- Node.js 16+ and npm
- Google API Key ([Get one here](https://aistudio.google.com/app/apikey))

### 1. Install Everything
```bash
./scripts/install.sh
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Start the Application
```bash
./scripts/run.sh
```

### 4. Open in Browser
- **Frontend (Chat UI)**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📱 Usage

1. The install script will set up both frontend and backend dependencies
2. Copy `.env.example` to `.env` and add your Google API key
3. Run `./scripts/run.sh` to start both servers simultaneously
4. Open http://localhost:5173 for the chat interface
5. Start chatting with your AI agent!

## 💬 Example Conversations

- "What's the latest news about AI?" (searches the web)
- "Explain quantum computing in simple terms"
- "Write a Python function to calculate fibonacci numbers"
- "What's the weather like today?"

## 🔧 Development

### Run Components Separately

**Backend only:**
```bash
cd backend
python3 app.py
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

### Project Structure Details

- **Backend (`backend/`)**:
  - `app.py` - FastAPI application with CORS and error handling
  - `agent.py` - Agno agent factory with fallback mechanisms
  - `config.py` - Centralized configuration management
  - `requirements.txt` - Python dependencies

- **Frontend (`frontend/`)**:
  - `src/App.tsx` - Main React chat component with TypeScript
  - `src/config.ts` - Frontend configuration and API settings
  - Tailwind CSS for styling, Vite for building

- **Scripts (`scripts/`)**:
  - `install.sh` - Automated dependency installation
  - `run.sh` - Start both services with health checks
  - `uninstall.sh` - Clean project and remove dependencies

## 🎛️ Configuration

### Backend Configuration (`backend/config.py`)
- API host/port settings
- CORS origins for production
- Model and tool configurations
- Environment-specific settings

### Frontend Configuration (`frontend/src/config.ts`)
- API base URL
- UI behavior settings
- Performance optimizations

## 🔌 API Endpoints

- `GET /` - API information
- `POST /chat` - Send message to agent
- `GET /health` - Comprehensive health check
- `GET /docs` - Interactive API documentation

## 🚀 Customization

### Modify Agent Behavior
Edit instructions in `backend/agent.py`:

```python
instructions=[
    "You are a helpful AI assistant...",
    "Add custom instructions here...",
]
```

### Add More Tools
```python
from agno.tools.calculator import Calculator
from agno.tools.python import PythonTools

tools=[DuckDuckGoTools(), Calculator(), PythonTools()]
```

### Frontend Styling
The React frontend uses Tailwind CSS. Modify `frontend/src/App.tsx` or add custom CSS.

## 🐛 Troubleshooting

### Common Issues

**Agent Not Initialized:**
- Check that `GOOGLE_API_KEY` is set in `.env`
- Verify API key is valid at https://aistudio.google.com/app/apikey

**Port Already in Use:**
- Backend (8000): Modify `API_PORT` in `backend/config.py`
- Frontend (5173): Vite will automatically use next available port

**Dependencies Missing:**
```bash
./scripts/install.sh  # Reinstall everything
```

**Rate Limiting:**
- The agent gracefully handles DuckDuckGo rate limits
- Fallback responses provided when search fails

### Clean Installation
```bash
./scripts/uninstall.sh  # Clean everything
./scripts/install.sh    # Reinstall
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `./scripts/run.sh`
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License. 