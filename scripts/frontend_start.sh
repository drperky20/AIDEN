#!/bin/bash

echo "🚀 Starting Frontend Application..."
echo "------------------------------------"
echo "⏳ Please wait while the Next.js development server starts."
echo ""
echo "🕒 This might take a few moments..."
echo ""

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to the frontend directory relative to the script's location
cd "$SCRIPT_DIR/../frontend" || { echo "❌ Error: Could not navigate to frontend directory."; exit 1; }

echo "✨ Frontend development server starting..."
echo "✨ Access it at: http://localhost:3000"
echo "✨ (Usually CMD+click or CTRL+click on the link in your terminal)"
echo "------------------------------------"
echo ""

# Start the frontend development server
# Assuming npm is used. If you use yarn or another manager,
# you might need to change 'npm run dev'.
npm run dev

echo "🚪 Frontend server process exited." 