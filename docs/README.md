# AIDEN V2: Personal AI Assistant

AIDEN (AI Development ENvironment) is a powerful, extensible personal AI assistant built on the Agno framework and powered by Google's Gemini models. It's designed to be your Jarvis-like companion, capable of natural conversation, web search, file operations, and more.

## Key Features

- **Agno-Powered**: Built on the lightweight, fast [Agno framework](https://github.com/agno-ai/agno) for AI agents
- **Gemini Models**: Leverages Google's powerful Gemini models for high-quality responses
- **Streaming Responses**: Real-time streaming of agent responses, including intermediate steps
- **Long-term Memory**: Remembers conversation history and user preferences
- **Extensible Tools**: Dynamic tool loading system for easy addition of new capabilities
- **Modern FastAPI Backend**: Clean, async API with proper error handling
- **Next.js Frontend**: (Coming soon) Sleek, responsive UI for interacting with AIDEN

## Architecture

AIDEN V2 follows Agno's progressive agent design:

1. **Level 1**: Single agent with tools (current implementation)
2. **Level 2**: Knowledge bases and storage (vector DB integration coming soon)
3. **Level 3**: Advanced memory and reasoning (planned)
4. **Level 4**: Teams of specialized agents (planned)
5. **Level 5**: Deterministic agent workflows (planned)

The codebase is organized into:

```
AIDEN/
├── backend/           # FastAPI backend
│   ├── agent/         # Agent definitions and factory
│   ├── api/           # API endpoints and server
│   ├── core/          # Core functionalities (memory, etc.)
│   └── tools/         # Custom agent tools
├── frontend/          # Next.js frontend (WIP)
├── data/              # Local data storage
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## Getting Started

See the [Setup Guide](./setup_guide.md) for detailed installation instructions.

### Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Edit `.env` and provide the required API keys
4. Run the development server:

```bash
# Start the backend API server
./scripts/run_dev.sh

# Start the frontend (if available)
./scripts/run_dev.sh frontend
```

## Roadmap

See the [Roadmap](./roadmap.md) for planned features and improvements.

## Contributing

Contributions are welcome! See the [Contributing Guide](./contributing.md) for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 