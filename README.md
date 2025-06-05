# 🤖 AIDEN - AI Personal Assistant

A beautiful, intelligent command-line assistant powered by Google Gemini and the Agno framework.

## ✨ Features

- 🎨 **Beautiful CLI Interface** - Rich terminal UI with colors, animations, and intuitive commands
- 🧠 **Google Gemini Integration** - Advanced AI capabilities with streaming responses
- 🔧 **Powerful Tools** - Web search, file operations, GitHub integration, and more
- 💾 **Persistent Memory** - Conversation history and context awareness
- 🌐 **Universal API** - FastAPI backend for future network and web integrations
- ⚡ **Optimized for M1 Macs** - Efficient memory usage and local-first approach

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini
- 8GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AIDEN
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

5. **Start AIDEN**
   ```bash
   python aiden_cli.py chat
   ```

## 🎯 CLI Commands

### Main Commands

- `python aiden_cli.py chat` - Start interactive chat with AIDEN
- `python aiden_cli.py status` - Show system health and status
- `python aiden_cli.py config` - Manage configuration settings
- `python aiden_cli.py version` - Show version information

### Chat Commands

Once in chat mode, you can use these commands:

- `/help` - Show available commands
- `/clear` - Clear the screen
- `/history` - Show conversation history
- `/status` - System status check
- `/tools` - List available tools
- `/export` - Export chat to file
- `/session [id]` - Switch chat session
- `/quit` - Exit the application

### Configuration Commands

```bash
# Show current configuration
python aiden_cli.py config --show

# Set Google API key
python aiden_cli.py config --api-key "your-api-key-here"

# Configure backend server
python aiden_cli.py config --backend-host localhost --backend-port 8000
```

### Status Monitoring

```bash
# One-time status check
python aiden_cli.py status

# Watch mode (updates every 5 seconds)
python aiden_cli.py status --watch

# Custom update interval
python aiden_cli.py status --watch --interval 10
```

## 🏗️ Architecture

```
AIDEN/
├── cli/                    # Beautiful CLI interface
│   ├── components/         # Chat, status, and UI components
│   ├── utils/             # Styling and helper utilities
│   └── main.py            # CLI entry point
├── backend/               # FastAPI server and business logic
│   ├── api/               # REST API endpoints
│   ├── core/              # Core functionality
│   ├── agent/             # AI agent implementation
│   └── tools/             # Available tools and integrations
├── scripts/               # Automation and utility scripts
└── aiden.py              # Main application entry point
```

### Design Philosophy

- **CLI-First**: Beautiful terminal interface for daily use
- **Universal API**: FastAPI backend enables future web/mobile clients
- **Memory Efficient**: Optimized for 8GB RAM with local-first approach
- **Extensible**: Modular architecture for easy feature additions

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False

# Agent Settings
ENABLE_WEB_SEARCH=True
SHOW_TOOL_CALLS=True
ENABLE_MARKDOWN=True
MAX_HISTORY_MESSAGES=5

# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///../data/aiden_memory.db

# Optional: Mem0 for advanced memory features
MEM0_API_KEY=your_mem0_api_key_here
```

### Getting API Keys

1. **Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

2. **Mem0 API Key (Optional)**
   - Visit [Mem0 Platform](https://mem0.ai)
   - Sign up and get your API key
   - Enables advanced memory features

## 🚀 Usage Examples

### Basic Chat

```bash
python aiden_cli.py chat
```

### Remote Backend

```bash
python aiden_cli.py chat --backend-url http://your-server:8000 --no-auto-start-backend
```

### Status Monitoring

```bash
# Quick status check
python aiden_cli.py status

# Continuous monitoring
python aiden_cli.py status --watch --interval 5
```

### Configuration Management

```bash
# View current settings
python aiden_cli.py config --show

# Update API key
python aiden_cli.py config --api-key "new-key"

# Change backend settings
python aiden_cli.py config --backend-host 192.168.1.100 --backend-port 9000
```

## 🛠️ Development

### Running the Backend Separately

```bash
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Adding New Tools

1. Create your tool in `backend/tools/`
2. Register it in the agent configuration
3. The CLI will automatically discover and display it

### Customizing the CLI

- **Themes**: Edit `cli/utils/styling.py`
- **Components**: Add new components in `cli/components/`
- **Commands**: Extend `cli/main.py`

## 📊 Performance

Optimized for macOS with limited RAM:

- **Memory Usage**: < 4GB during operation
- **Startup Time**: < 2 seconds
- **Response Time**: Sub-second for most operations
- **Local Storage**: SQLite for efficient data management

### Mac M1 Specific Tips

- AIDEN now uses `uvloop` when available for a faster event loop on Unix/Mac.
- The Whisper STT automatically selects `int8` compute on Apple Silicon for
  reduced latency.
- When installing dependencies, use Homebrew Python or ensure arm64 wheels are
  used for optimal performance.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Run `python aiden_cli.py status` to diagnose problems
3. Check your API keys and configuration
4. Open an issue on GitHub

---

**Built with ❤️ for productivity and intelligence.**
