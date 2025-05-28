import subprocess
import webbrowser
import os
import time

def print_header():
    """Prints a fancy header for the CLI."""
    print("**********************************************")
    print("*                                            *")
    print("*      🚀 AIDEN Development Launcher 🚀      *")
    print("*                                            *")
    print("**********************************************")
    print("\n")

def open_url_after_delay(url, delay=3):
    """Opens a URL in the default web browser after a delay."""
    print(f"🕒 Attempting to open {url} in your browser in {delay} seconds...")
    time.sleep(delay)
    try:
        webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible
        print(f"✅ Successfully opened {url}")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"   Please manually open: {url}")

def run_script(script_name, open_url=None, title="Application"):
    """Runs a shell script and optionally opens a URL."""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Error: Script not found at {script_path}")
        return

    print(f"🏃 Running {title} ({script_name})...")
    print("----------------------------------------------------")
    
    try:
        # For macOS, we can open a new terminal window for each server
        # For other OS, it will run in the current terminal
        if os.name == 'posix': # Covers macOS and Linux
            # Check if we are on macOS specifically for terminal opening behavior
            if 'darwin' in os.uname().sysname.lower():
                process = subprocess.Popen(['open', '-a', 'Terminal', script_path])
            else: # For Linux, run in background or handle differently if needed
                  # This basic version runs it in the current window and blocks.
                  # For a more advanced CLI, you might use libraries like 'tmux' or run in background.
                process = subprocess.Popen(['bash', script_path])
        else: # For Windows
            process = subprocess.Popen(['cmd', '/c', script_path], shell=True)
        
        print(f"✨ {title} server process started (PID: {process.pid}).")
        print(f"✨ Check the new terminal window (on macOS) or this window for logs.")

        if open_url:
            open_url_after_delay(open_url)
            
    except FileNotFoundError:
        print(f"❌ Error: The script '{script_path}' was not found.")
        print(f"   Please ensure it exists and is executable.")
    except Exception as e:
        print(f"❌ An error occurred while trying to run {script_name}: {e}")
    
    print("----------------------------------------------------\n")


def main_menu():
    """Displays the main menu and handles user input."""
    print_header()
    
    while True:
        print("Please choose an option:")
        print("  1. Start Frontend (Next.js on http://localhost:3000)")
        print("  2. Start Backend (Python/FastAPI on http://localhost:8000)")
        print("  3. Start Both Frontend and Backend")
        print("  4. Open Frontend in browser (http://localhost:3000)")
        print("  5. Open Backend docs in browser (e.g., http://localhost:8000/docs)")
        print("  0. Exit")
        print("\n")
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            run_script("frontend_start.sh", open_url="http://localhost:3000", title="Frontend")
        elif choice == '2':
            run_script("backend_start.sh", open_url="http://localhost:8000/docs", title="Backend") # Assuming /docs for FastAPI
        elif choice == '3':
            print("🚀 Starting both Frontend and Backend...")
            run_script("frontend_start.sh", open_url="http://localhost:3000", title="Frontend")
            print("--- Waiting a moment before starting backend ---")
            time.sleep(2) # Brief pause
            run_script("backend_start.sh", open_url="http://localhost:8000/docs", title="Backend")
        elif choice == '4':
            open_url_after_delay("http://localhost:3000")
        elif choice == '5':
            open_url_after_delay("http://localhost:8000/docs") # Or whatever your backend's main page is
        elif choice == '0':
            print("👋 Exiting AIDEN Development Launcher. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.\n")
        
        print("\nPress Enter to return to the menu...")
        input()
        # Clear screen for better readability (optional, works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header()

if __name__ == "__main__":
    # Ensure scripts are executable
    script_dir = os.path.dirname(__file__)
    frontend_script = os.path.join(script_dir, "frontend_start.sh")
    backend_script = os.path.join(script_dir, "backend_start.sh")

    if os.path.exists(frontend_script):
        os.chmod(frontend_script, 0o755)
    if os.path.exists(backend_script):
        os.chmod(backend_script, 0o755)
        
    main_menu() 