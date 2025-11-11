#!/bin/bash

# Google Gemini API Integration Setup Script
echo "🤖 Setting up Google Gemini API integration for Smart Building LLM agents..."

# Change to backend directory
cd backend || exit 1

# Install new dependencies
echo "📦 Installing Google Generative AI and HTTP client dependencies..."
pip install google-generativeai httpx

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected. Consider using one."
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "🔑 IMPORTANT: You need to get a free Google AI API key!"
    echo ""
    echo "1. Visit: https://aistudio.google.com/app/apikey"
    echo "2. Create a new API key (free tier available)"
    echo "3. Add it to your .env file:"
    echo "   GOOGLE_API_KEY=your_actual_api_key_here"
    echo ""
else
    echo "✅ .env file exists"
fi

# Test the installation
echo ""
echo "🧪 Testing Google Generative AI installation..."
python3 -c "
import sys
try:
    import google.generativeai as genai
    print('✅ google-generativeai installed successfully')
except ImportError as e:
    print(f'❌ Failed to import google-generativeai: {e}')
    sys.exit(1)

try:
    import httpx
    print('✅ httpx installed successfully')
except ImportError as e:
    print(f'❌ Failed to import httpx: {e}')
    sys.exit(1)

print('✅ All LLM dependencies installed successfully!')
"

echo ""
echo "🚀 LLM Integration Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Add your Google API key to the .env file"
echo "2. Start the backend server: uvicorn app.main:app --reload"
echo "3. Test LLM integration at: http://localhost:8000/api/llm/status"
echo "4. View API docs at: http://localhost:8000/docs"
echo ""
echo "🎯 Your smart building now has an AI brain powered by Google Gemini!"