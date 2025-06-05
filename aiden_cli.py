#!/usr/bin/env python3
"""
AIDEN CLI - AI Personal Assistant
Enhanced interface with voice mode, streaming, and advanced tool integration

Features:
- Chat Mode: Text-based conversation with streaming responses
- Voice Mode: Real-time voice conversation with STT/TTS
- OpenRouter Integration: Fast Llama 4 Maverick (FREE model)
- ElevenLabs TTS: High-quality voice synthesis
- Faster-Whisper STT: Real-time speech recognition

Run: python aiden_cli.py
"""

import asyncio
import json
import os
import sys
import httpx
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, AsyncGenerator
import logging

# Rich imports for beautiful CLI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.markdown import Markdown
from rich.columns import Columns

# Configure logging to be less verbose
logging.basicConfig(level=logging.WARNING)

class AidenCLI:
    def __init__(self):
        self.console = Console()
        self.backend_url = "http://localhost:8000"
        self.session_id = "main"
        self.conversation_history = []
        self.voice_mode_active = False
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_header(self):
        """Display the enhanced AIDEN header"""
        header = Panel(
            Align.center(
                Text("🤖 AIDEN V2 - AI Personal Assistant", style="bold cyan") + "\n" +
                Text("Powered by OpenRouter (Llama 4 Maverick) + ElevenLabs Voice", style="dim") + "\n\n" +
                Text("Your intelligent CLI companion with voice capabilities", style="italic")
            ),
            style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header)
        self.console.print()

    async def check_backend_status(self) -> Dict[str, Any]:
        """Check backend status including voice capabilities"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check basic health
                health_response = await client.get(f"{self.backend_url}/health")
                if health_response.status_code != 200:
                    return {"status": "offline", "voice_available": False}
                
                health_data = health_response.json()
                
                # Check voice status
                try:
                    voice_response = await client.get(f"{self.backend_url}/voice/status")
                    voice_data = voice_response.json() if voice_response.status_code == 200 else {}
                except:
                    voice_data = {"voice_mode_available": False}
                
                return {
                    "status": "online",
                    "health": health_data,
                    "voice_available": voice_data.get("voice_mode_available", False),
                    "voice_config": voice_data.get("configuration", {})
                }
        except:
            return {"status": "offline", "voice_available": False}

    async def start_backend(self) -> bool:
        """Start the backend server with enhanced monitoring"""
        self.console.print("🚀 Starting AIDEN backend...", style="yellow")
        
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path.cwd())
            
            # Start the backend process
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "backend.api.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--log-level", "warning"
            ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for backend to start with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
            ) as progress:
                task = progress.add_task("Starting backend...", total=10)
                
                for i in range(10):
                    await asyncio.sleep(1)
                    progress.update(task, advance=1)
                    
                    status = await self.check_backend_status()
                    if status["status"] == "online":
                        progress.update(task, description="✅ Backend started successfully!")
                        self.console.print("✅ Backend online with voice capabilities!" if status["voice_available"] else "✅ Backend online (voice configuration needed)", style="green")
                        return True
            
            self.console.print("❌ Failed to start backend", style="red")
            return False
            
        except Exception as e:
            self.console.print(f"❌ Error starting backend: {e}", style="red")
            return False

    def check_env_configuration(self) -> Dict[str, bool]:
        """Check current environment configuration"""
        env_path = Path(".env")
        config_status = {
            "env_exists": env_path.exists(),
            "openrouter_configured": False,
            "elevenlabs_configured": False,
            "google_configured": False
        }
        
        if env_path.exists():
            with open(env_path) as f:
                content = f.read()
                config_status["openrouter_configured"] = "OPENROUTER_API_KEY=" in content and not "your_openrouter" in content
                config_status["elevenlabs_configured"] = "ELEVENLABS_API_KEY=" in content and not "your_elevenlabs" in content
                config_status["google_configured"] = "GOOGLE_API_KEY=" in content and not "your_google" in content
        
        return config_status

    async def show_config_menu(self):
        """Enhanced configuration menu with voice setup"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("⚙️  AIDEN Configuration", style="bold yellow")
        self.console.print()
        
        # Check current configuration
        config_status = self.check_env_configuration()
        backend_status = await self.check_backend_status()
        
        # Configuration status table
        config_table = Table(title="Configuration Status", show_header=True, header_style="bold magenta")
        config_table.add_column("Component", style="cyan", width=20)
        config_table.add_column("Status", width=15)
        config_table.add_column("Details", style="dim")
        
        # OpenRouter status
        or_status = "✅ Configured" if config_status["openrouter_configured"] else "❌ Not configured"
        or_details = "Llama 4 Maverick (FREE)" if config_status["openrouter_configured"] else "Get from openrouter.ai"
        config_table.add_row("OpenRouter API", or_status, or_details)
        
        # ElevenLabs status
        el_status = "✅ Configured" if config_status["elevenlabs_configured"] else "❌ Not configured"
        el_details = "Voice synthesis ready" if config_status["elevenlabs_configured"] else "Get from elevenlabs.io"
        config_table.add_row("ElevenLabs API", el_status, el_details)
        
        # Google status
        google_status = "✅ Configured" if config_status["google_configured"] else "❌ Not configured"
        google_details = "Fallback model ready" if config_status["google_configured"] else "Get from aistudio.google.com"
        config_table.add_row("Google Gemini", google_status, google_details)
        
        # Backend status
        backend_text = "✅ Online" if backend_status["status"] == "online" else "❌ Offline"
        backend_details = f"Voice: {'Available' if backend_status.get('voice_available') else 'Unavailable'}"
        config_table.add_row("Backend Server", backend_text, backend_details)
        
        self.console.print(config_table)
        self.console.print()
        
        # Configuration options
        options_panel = Panel(
            """[bold cyan]Configuration Options[/bold cyan]

[1] 🔧 Quick Setup (Run voice setup script)
[2] 📝 Manual API Key Entry
[3] 🧪 Test Current Configuration
[4] 📊 Show Detailed Status
[5] 🔙 Back to Main Menu

Choose an option (1-5):""",
            style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(options_panel)
        choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5"], default="1")
        
        if choice == "1":
            await self.run_voice_setup()
        elif choice == "2":
            await self.manual_api_setup()
        elif choice == "3":
            await self.test_configuration()
        elif choice == "4":
            await self.show_detailed_status()
        # Option 5 returns to main menu

    async def run_voice_setup(self):
        """Run the voice setup script"""
        self.console.print("🔧 Running AIDEN Voice Setup...", style="yellow")
        
        try:
            result = subprocess.run([sys.executable, "setup_voice.py"], 
                                  capture_output=False, text=True)
            
            if result.returncode == 0:
                self.console.print("✅ Voice setup completed!", style="green")
            else:
                self.console.print("❌ Voice setup encountered an error", style="red")
        except FileNotFoundError:
            self.console.print("❌ setup_voice.py not found. Please ensure it's in the current directory.", style="red")
        except Exception as e:
            self.console.print(f"❌ Error running setup: {e}", style="red")
        
        input("\nPress Enter to continue...")

    async def manual_api_setup(self):
        """Manual API key configuration"""
        self.console.print("📝 Manual API Key Configuration", style="yellow")
        self.console.print()
        
        config_status = self.check_env_configuration()
        env_path = Path(".env")
        
        # Read existing .env if present
        existing_content = ""
        if env_path.exists():
            with open(env_path) as f:
                existing_content = f.read()
        
        self.console.print("📋 API Key Sources:")
        self.console.print("   OpenRouter: https://openrouter.ai/ (FREE Llama 4 Maverick)")
        self.console.print("   ElevenLabs: https://elevenlabs.io/ (10k chars/month free)")
        self.console.print("   Google AI: https://aistudio.google.com/ (Free tier)")
        self.console.print()
        
        # Collect API keys
        updates = {}
        
        if not config_status["openrouter_configured"]:
            openrouter_key = Prompt.ask("OpenRouter API Key (or press Enter to skip)")
            if openrouter_key.strip():
                updates["OPENROUTER_API_KEY"] = openrouter_key.strip()
        
        if not config_status["elevenlabs_configured"]:
            elevenlabs_key = Prompt.ask("ElevenLabs API Key (or press Enter to skip)")
            if elevenlabs_key.strip():
                updates["ELEVENLABS_API_KEY"] = elevenlabs_key.strip()
        
        if not config_status["google_configured"]:
            google_key = Prompt.ask("Google API Key (or press Enter to skip)")
            if google_key.strip():
                updates["GOOGLE_API_KEY"] = google_key.strip()
        
        # Update .env file
        if updates:
            env_template = """# AIDEN V2 Configuration
USE_OPENROUTER=True
OPENROUTER_API_KEY={openrouter_key}
OPENROUTER_MODEL_ID=meta-llama/llama-4-maverick:free

GOOGLE_API_KEY={google_key}
GEMINI_MODEL_ID=gemini-1.5-flash-latest

ENABLE_VOICE_MODE=True
ELEVENLABS_API_KEY={elevenlabs_key}
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
ELEVENLABS_MODEL_ID=eleven_flash_v2_5

WHISPER_MODEL_SIZE=tiny.en
VOICE_ACTIVATION_THRESHOLD=0.02
MAX_SILENCE_DURATION=2.0

API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
ENABLE_WEB_SEARCH=True
SHOW_TOOL_CALLS=True
ENABLE_MARKDOWN=True
"""
            
            # Get current or default values
            openrouter_key = updates.get("OPENROUTER_API_KEY", "your_openrouter_api_key_here")
            elevenlabs_key = updates.get("ELEVENLABS_API_KEY", "your_elevenlabs_api_key_here")
            google_key = updates.get("GOOGLE_API_KEY", "your_google_api_key_here")
            
            env_content = env_template.format(
                openrouter_key=openrouter_key,
                elevenlabs_key=elevenlabs_key,
                google_key=google_key
            )
            
            with open(env_path, 'w') as f:
                f.write(env_content)
            
            self.console.print("✅ Configuration saved!", style="green")
        else:
            self.console.print("No changes made.", style="yellow")
        
        input("\nPress Enter to continue...")

    async def test_configuration(self):
        """Test current configuration"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("🧪 Testing AIDEN Configuration...", style="bold yellow")
        self.console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        ) as progress:
            
            # Test backend
            task1 = progress.add_task("Checking backend...", total=1)
            backend_status = await self.check_backend_status()
            
            if backend_status["status"] == "offline":
                progress.update(task1, description="Starting backend...")
                if not await self.start_backend():
                    self.console.print("❌ Cannot start backend", style="red")
                    input("Press Enter to continue...")
                    return
                backend_status = await self.check_backend_status()
            
            progress.update(task1, advance=1, description="✅ Backend online")
            
            # Test chat functionality
            task2 = progress.add_task("Testing chat...", total=1)
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.backend_url}/chat",
                        json={"message": "Hello! Just testing - respond with 'Test successful'", "session_id": "test"}
                    )
                    
                    if response.status_code == 200:
                        progress.update(task2, advance=1, description="✅ Chat working")
                        chat_working = True
                    else:
                        progress.update(task2, advance=1, description="❌ Chat failed")
                        chat_working = False
            except Exception:
                progress.update(task2, advance=1, description="❌ Chat error")
                chat_working = False
            
            # Test voice if available
            if backend_status.get("voice_available"):
                task3 = progress.add_task("Testing voice...", total=1)
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        voice_response = await client.post(
                            f"{self.backend_url}/voice/tts",
                            json={"text": "Test"}
                        )
                        voice_working = voice_response.status_code == 200
                        progress.update(task3, advance=1, description="✅ Voice working" if voice_working else "❌ Voice failed")
                except Exception:
                    progress.update(task3, advance=1, description="❌ Voice error")
                    voice_working = False
            else:
                voice_working = False
        
        # Show results
        self.console.print()
        results_table = Table(title="Test Results", show_header=True)
        results_table.add_column("Component", style="cyan")
        results_table.add_column("Status", style="green")
        results_table.add_column("Details", style="dim")
        
        results_table.add_row("Backend", "✅ Online" if backend_status["status"] == "online" else "❌ Offline", "Core system")
        results_table.add_row("Chat", "✅ Working" if chat_working else "❌ Failed", "Text conversation")
        results_table.add_row("Voice", "✅ Working" if voice_working else "❌ Not available", "TTS/STT capabilities")
        
        self.console.print(results_table)
        input("\nPress Enter to continue...")

    async def show_detailed_status(self):
        """Show detailed system status"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("📊 Detailed System Status", style="bold yellow")
        self.console.print()
        
        # Get comprehensive status
        backend_status = await self.check_backend_status()
        config_status = self.check_env_configuration()
        
        # Backend status
        if backend_status["status"] == "online":
            health_data = backend_status.get("health", {})
            
            backend_panel = Panel(
                f"""Status: ✅ Online
Tools: {health_data.get('tools_count', 'Unknown')} loaded
Model: {health_data.get('model_info', 'Not specified')}
Uptime: {health_data.get('uptime', 'Unknown')}""",
                title="🖥️  Backend Server",
                style="green"
            )
        else:
            backend_panel = Panel(
                "Status: ❌ Offline\nPlease start the backend server.",
                title="🖥️  Backend Server",
                style="red"
            )
        
        # Voice status
        if backend_status.get("voice_available"):
            voice_config = backend_status.get("voice_config", {})
            voice_panel = Panel(
                f"""Status: ✅ Available
Voice ID: {voice_config.get('voice_id', 'Not configured')}
Model: {voice_config.get('elevenlabs_model', 'Not configured')}
Whisper: {voice_config.get('whisper_model', 'Not configured')}""",
                title="🎤 Voice System",
                style="green"
            )
        else:
            voice_panel = Panel(
                "Status: ❌ Not available\nConfigure ElevenLabs API key to enable voice mode.",
                title="🎤 Voice System",
                style="red"
            )
        
        # API configuration
        api_status_lines = []
        api_status_lines.append(f"OpenRouter: {'✅ Configured' if config_status['openrouter_configured'] else '❌ Missing'}")
        api_status_lines.append(f"ElevenLabs: {'✅ Configured' if config_status['elevenlabs_configured'] else '❌ Missing'}")
        api_status_lines.append(f"Google: {'✅ Configured' if config_status['google_configured'] else '❌ Missing'}")
        
        api_panel = Panel(
            "\n".join(api_status_lines),
            title="🔑 API Keys",
            style="blue"
        )
        
        # Display panels in columns
        self.console.print(Columns([backend_panel, voice_panel]))
        self.console.print()
        self.console.print(api_panel)
        
        input("\nPress Enter to continue...")

    async def start_voice_mode(self):
        """Start voice conversation mode"""
        self.clear_screen()
        self.show_header()
        
        # Check voice availability
        backend_status = await self.check_backend_status()
        if not backend_status.get("voice_available"):
            self.console.print("❌ Voice mode not available. Please configure ElevenLabs API key.", style="red")
            input("Press Enter to continue...")
            return
        
        self.console.print("🎤 Voice Mode - Real-time Conversation", style="bold green")
        self.console.print("Speak naturally, AIDEN will respond with voice", style="dim")
        self.console.print("Press Ctrl+C to stop voice mode", style="dim")
        self.console.print("=" * 60)
        self.console.print()
        
        # Start voice mode
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.backend_url}/voice/start-voice-mode")
                if response.status_code != 200:
                    self.console.print("❌ Failed to start voice mode", style="red")
                    input("Press Enter to continue...")
                    return
            
            self.voice_mode_active = True
            
            with Live("🎤 Listening... (Speak now)", console=self.console, refresh_per_second=4) as live:
                self.console.print("Voice mode active! Speak to AIDEN...")
                
                # This would normally handle WebSocket connection for real-time voice
                # For now, we'll show a placeholder interface
                await asyncio.sleep(2)
                live.update("🔊 Voice mode ready - implement WebSocket client here")
                
                # Wait for user to interrupt
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            self.console.print("\n\n🔇 Voice mode stopped", style="yellow")
        except Exception as e:
            self.console.print(f"\n❌ Voice mode error: {e}", style="red")
        finally:
            # Stop voice mode
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(f"{self.backend_url}/voice/stop-voice-mode")
            except:
                pass
            self.voice_mode_active = False
            input("Press Enter to continue...")

    async def stream_chat_response(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat response from backend"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.backend_url}/chat-stream",
                    json={"message": message, "session_id": self.session_id},
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    if response.status_code != 200:
                        yield {"type": "error", "detail": f"Backend error: {response.status_code}"}
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            try:
                                event_data = line[6:]  # Remove "data: " prefix
                                if event_data.strip():
                                    event = json.loads(event_data)
                                    yield event
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                yield {"type": "error", "detail": f"Parse error: {e}"}
        except Exception as e:
            yield {"type": "error", "detail": f"Connection error: {e}"}

    async def start_chat(self):
        """Enhanced chat interface with improved streaming"""
        self.clear_screen()
        self.show_header()
        
        # Check backend
        backend_status = await self.check_backend_status()
        if backend_status["status"] == "offline":
            if not await self.start_backend():
                self.console.print("❌ Cannot start backend. Please check your configuration.", style="red")
                input("Press Enter to continue...")
                return
        
        self.console.print("💬 Chat with AIDEN", style="bold green")
        self.console.print("Type 'quit', 'exit', or 'voice' to change modes", style="dim")
        
        # Show current model info
        if backend_status.get("health", {}).get("model_info"):
            self.console.print(f"Model: {backend_status['health']['model_info']}", style="dim")
        
        self.console.print("=" * 60)
        self.console.print()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'voice':
                    await self.start_voice_mode()
                    self.clear_screen()
                    self.show_header()
                    self.console.print("💬 Chat with AIDEN", style="bold green")
                    self.console.print("Type 'quit', 'exit', or 'voice' to change modes", style="dim")
                    self.console.print("=" * 60)
                    continue
                
                if not user_input.strip():
                    continue
                
                # Add to history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "agent": ""
                })
                
                # Show streaming response
                self.console.print()
                
                # Enhanced streaming display
                thinking_panel = Panel("🤔 Thinking...", title="AIDEN Status", style="yellow")
                response_text = ""
                
                with Live(thinking_panel, console=self.console, refresh_per_second=4) as live:
                    async for event in self.stream_chat_response(user_input):
                        event_type = event.get("type", "unknown")
                        
                        if event_type == "thinking_indicator":
                            content = event.get("content", "Thinking...")
                            live.update(Panel(f"🤔 {content}", title="AIDEN Status", style="yellow"))
                        
                        elif event_type == "tool_start":
                            tool_name = event.get("name", "Unknown")
                            tool_input = event.get("input", "")
                            tool_panel = Panel(
                                f"🔧 Using: {tool_name}\nInput: {tool_input[:100]}{'...' if len(tool_input) > 100 else ''}",
                                title="Tool Execution",
                                style="blue"
                            )
                            live.update(tool_panel)
                        
                        elif event_type == "tool_end":
                            tool_name = event.get("name", "Unknown")
                            result = event.get("result", "")
                            tool_panel = Panel(
                                f"✅ Completed: {tool_name}\nResult: {result[:200]}{'...' if len(result) > 200 else ''}",
                                title="Tool Result",
                                style="green"
                            )
                            live.update(tool_panel)
                            await asyncio.sleep(1)  # Show result briefly
                        
                        elif event_type == "llm_chunk":
                            chunk = event.get("content", "")
                            response_text += chunk
                            
                            # Update with streaming response
                            response_panel = Panel(
                                response_text + "▋",  # Add cursor
                                title="🤖 AIDEN",
                                style="bright_green"
                            )
                            live.update(response_panel)
                        
                        elif event_type == "final_response":
                            final_content = event.get("content", response_text)
                            if final_content:
                                response_text = final_content
                            
                            # Final response without cursor
                            final_panel = Panel(
                                response_text,
                                title="🤖 AIDEN",
                                style="bright_green"
                            )
                            live.update(final_panel)
                            break
                        
                        elif event_type == "error":
                            error_detail = event.get("detail", "Unknown error")
                            error_panel = Panel(
                                f"❌ Error: {error_detail}",
                                title="Error",
                                style="red"
                            )
                            live.update(error_panel)
                            break
                
                # Update conversation history
                if response_text and self.conversation_history:
                    self.conversation_history[-1]["agent"] = response_text
                
            except KeyboardInterrupt:
                self.console.print("\n\n👋 Chat interrupted. Returning to menu...", style="yellow")
                break
            except Exception as e:
                self.console.print(f"\n❌ Error: {e}", style="red")

    def export_logs(self):
        """Export conversation logs"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("📁 Export Conversation Logs", style="bold yellow")
        self.console.print()
        
        if not self.conversation_history:
            self.console.print("No conversation history to export.", style="yellow")
            input("Press Enter to continue...")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aiden_chat_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "exported_at": datetime.now().isoformat(),
                    "session_id": self.session_id,
                    "conversation_count": len(self.conversation_history),
                    "conversation": self.conversation_history
                }, f, indent=2)
            
            self.console.print(f"✅ Logs exported to: {filename}", style="green")
            self.console.print(f"   {len(self.conversation_history)} conversation entries saved", style="dim")
        except Exception as e:
            self.console.print(f"❌ Export failed: {e}", style="red")
        
        input("Press Enter to continue...")

    def show_main_menu(self):
        """Display the enhanced main menu"""
        self.clear_screen()
        self.show_header()
        
        menu_panel = Panel(
            """[bold cyan]AIDEN V2 Main Menu[/bold cyan]

[1] ⚙️  Configure AIDEN (API Keys & Voice Setup)
[2] 🧪 Test System (Backend, Chat, Voice)
[3] 💬 Start Text Chat (Streaming conversation)
[4] 🎤 Start Voice Mode (Real-time voice chat)
[5] 📁 Export Logs (Save conversation history)
[6] 📊 System Status (Detailed status view)
[7] 🚪 Exit

Choose an option (1-7):""",
            style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)

    async def run(self):
        """Enhanced main application loop"""
        while True:
            try:
                self.show_main_menu()
                choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5", "6", "7"], default="3")
                
                if choice == "1":
                    await self.show_config_menu()
                elif choice == "2":
                    await self.test_configuration()
                elif choice == "3":
                    await self.start_chat()
                elif choice == "4":
                    await self.start_voice_mode()
                elif choice == "5":
                    self.export_logs()
                elif choice == "6":
                    await self.show_detailed_status()
                elif choice == "7":
                    self.console.print("\n👋 Goodbye! Thank you for using AIDEN!", style="bright_cyan")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n\n👋 Goodbye! Thank you for using AIDEN!", style="bright_cyan")
                break
            except Exception as e:
                self.console.print(f"\n❌ Error: {e}", style="red")
                input("Press Enter to continue...")

async def main():
    """Enhanced entry point with dependency checking"""
    try:
        # Install required packages if missing
        try:
            import rich
            import httpx
        except ImportError:
            print("📦 Installing required packages...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "httpx"])
            print("✅ Packages installed!")
        
        print("🚀 Starting AIDEN V2 CLI...")
        app = AidenCLI()
        await app.run()
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 