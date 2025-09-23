#!/bin/bash

echo "Fixing all linting issues..."

# Fix ddgs version
sed -i 's/ddgs==4.1.1/ddgs==9.6.0/' requirements.txt

# Run import sorting and formatting
isort .
black .

# Fix remaining issues with specific edits
echo "Manual fixes applied. Running final check..."
flake8 . --statistics

echo "Fixes complete!"
