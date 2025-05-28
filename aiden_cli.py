#!/usr/bin/env python3
"""
AIDEN CLI - AI Personal Assistant
Single-file, streamlined interface with real streaming and tool integration

Run: python aiden_cli.py
"""

import asyncio
import json
import os
import sys
import httpx
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
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

# Configure logging to be less verbose
logging.basicConfig(level=logging.WARNING)

class AidenCLI:
    def __init__(self):
        self.console = Console()
        self.backend_url = "http://localhost:8000"
        self.session_id = "main"
        self.conversation_history = []
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_header(self):
        """Display the AIDEN header"""
        header = Panel(
            Align.center(
                Text("🤖 AIDEN AI Personal Assistant", style="bold cyan") + "\n" +
                Text("Powered by Google Gemini", style="dim") + "\n\n" +
                Text("Your intelligent CLI companion", style="italic")
            ),
            style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header)
        self.console.print()

    async def check_backend_status(self) -> bool:
        """Check if the backend is running"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.backend_url}/health")
                return response.status_code == 200
        except:
            return False

    async def start_backend(self) -> bool:
        """Start the backend server"""
        self.console.print("🚀 Starting AIDEN backend...", style="yellow")
        
        # Try to start the backend
        try:
            import subprocess
            import time
            
            # Start the backend process
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path.cwd())
            
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "backend.api.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--log-level", "warning"
            ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for backend to start
            for i in range(10):
                await asyncio.sleep(1)
                if await self.check_backend_status():
                    self.console.print("✅ Backend started successfully!", style="green")
                    return True
            
            self.console.print("❌ Failed to start backend", style="red")
            return False
            
        except Exception as e:
            self.console.print(f"❌ Error starting backend: {e}", style="red")
            return False

    def show_config_menu(self):
        """Show configuration options"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("⚙️  Configuration", style="bold yellow")
        self.console.print()
        
        # Check current configuration
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                content = f.read()
                has_api_key = "GOOGLE_API_KEY=" in content and not "your_" in content
        else:
            has_api_key = False
        
        # Show current status
        status_table = Table(show_header=False, box=None)
        status_table.add_column("Setting", style="cyan")
        status_table.add_column("Status", style="green" if has_api_key else "red")
        
        status_table.add_row("Google API Key", "✅ Configured" if has_api_key else "❌ Not configured")
        status_table.add_row("Backend URL", self.backend_url)
        status_table.add_row("Session ID", self.session_id)
        
        self.console.print(status_table)
        self.console.print()
        
        if not has_api_key:
            self.console.print("⚠️  You need to configure your Google API key first!", style="yellow")
            self.console.print("Get your API key from: https://aistudio.google.com/app/apikey", style="dim")
            self.console.print()
            
            api_key = Prompt.ask("Enter your Google API Key")
            if api_key and not api_key.startswith("your"):
                # Create or update .env file
                env_content = f"""# AIDEN Configuration
GOOGLE_API_KEY={api_key}
GEMINI_MODEL_ID=gemini-1.5-flash-latest
ENABLE_WEB_SEARCH=True
SHOW_TOOL_CALLS=True
ENABLE_MARKDOWN=True
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
"""
                with open(".env", "w") as f:
                    f.write(env_content)
                
                self.console.print("✅ Configuration saved!", style="green")
            else:
                self.console.print("❌ Invalid API key", style="red")
        
        input("\nPress Enter to continue...")

    async def test_aiden(self):
        """Test AIDEN functionality"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("🧪 Testing AIDEN...", style="bold yellow")
        self.console.print()
        
        # Check backend
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Checking backend...", total=None)
            
            if not await self.check_backend_status():
                progress.update(task, description="Starting backend...")
                if not await self.start_backend():
                    self.console.print("❌ Cannot start backend", style="red")
                    input("Press Enter to continue...")
                    return
            
            progress.update(task, description="Testing chat...")
            
            # Test a simple message
            try:
                test_message = "Hello! Just testing - respond with exactly 'Test successful'"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.backend_url}/chat",
                        json={"message": test_message, "session_id": "test"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.console.print("✅ AIDEN is working!", style="green")
                        self.console.print(f"Response: {result.get('response', 'No response')}", style="dim")
                    else:
                        self.console.print(f"❌ Test failed: {response.status_code}", style="red")
                        
            except Exception as e:
                self.console.print(f"❌ Test failed: {e}", style="red")
        
        input("\nPress Enter to continue...")

    def export_logs(self):
        """Export conversation logs"""
        self.clear_screen()
        self.show_header()
        
        self.console.print("📁 Export Logs", style="bold yellow")
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
                    "conversation": self.conversation_history
                }, f, indent=2)
            
            self.console.print(f"✅ Logs exported to: {filename}", style="green")
        except Exception as e:
            self.console.print(f"❌ Export failed: {e}", style="red")
        
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
        """Start the main chat interface"""
        self.clear_screen()
        self.show_header()
        
        # Check backend
        if not await self.check_backend_status():
            if not await self.start_backend():
                self.console.print("❌ Cannot start backend. Please check your configuration.", style="red")
                input("Press Enter to continue...")
                return
        
        self.console.print("💬 Chat with AIDEN", style="bold green")
        self.console.print("Type 'quit' or 'exit' to return to menu", style="dim")
        self.console.print("=" * 60)
        self.console.print()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
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
                
                # Create panels for different types of information
                thinking_panel = Panel("🤔 Thinking...", title="AIDEN Status", style="yellow")
                tool_panel = None
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

    def show_main_menu(self):
        """Display the main menu"""
        self.clear_screen()
        self.show_header()
        
        menu_panel = Panel(
            """[bold cyan]Main Menu[/bold cyan]

[1] ⚙️  Configure AIDEN
[2] 🧪 Test AIDEN
[3] 💬 Start Chat
[4] 📁 Export Logs
[5] 🚪 Exit

Choose an option (1-5):""",
            style="bright_blue",
            padding=(1, 2)
        )
        
        self.console.print(menu_panel)

    async def run(self):
        """Main application loop"""
        while True:
            try:
                self.show_main_menu()
                choice = Prompt.ask("Choice", choices=["1", "2", "3", "4", "5"], default="3")
                
                if choice == "1":
                    self.show_config_menu()
                elif choice == "2":
                    await self.test_aiden()
                elif choice == "3":
                    await self.start_chat()
                elif choice == "4":
                    self.export_logs()
                elif choice == "5":
                    self.console.print("\n👋 Goodbye!", style="bright_cyan")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n\n👋 Goodbye!", style="bright_cyan")
                break
            except Exception as e:
                self.console.print(f"\n❌ Error: {e}", style="red")
                input("Press Enter to continue...")

async def main():
    """Entry point"""
    try:
        # Install required packages if missing
        try:
            import rich
            import httpx
        except ImportError:
            print("Installing required packages...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "httpx"])
            print("✅ Packages installed!")
        
        app = AidenCLI()
        await app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 