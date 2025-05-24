#!/bin/bash
echo "Adding all files to git..."
git add .
echo "Committing changes..."
git commit -m "Consolidate frontend into main repository

- Removed nested git repository from frontend/
- Added all frontend files to main project
- Fixed git configuration and remote references
- Repository now has single git root"
echo "Git operations completed successfully!" 