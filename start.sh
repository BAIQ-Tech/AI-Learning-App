#!/bin/bash

echo "🚀 Starting AI-Learning Application"
echo "=================================="

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the AI-Learning root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

if ! command_exists pip3; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ All dependencies found!"

# Setup backend
echo ""
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please add your OpenAI API key to backend/.env"
    echo "   Example: OPENAI_API_KEY=your_api_key_here"
fi

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "🗄️  Initializing database..."
python3 -c "from main import init_db; init_db(); print('Database initialized!')"

echo "🚀 Starting FastAPI backend on http://localhost:8000..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Setup frontend
echo ""
echo "⚛️  Setting up React frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

echo "🚀 Starting React frontend on http://localhost:3000..."
npm start &
FRONTEND_PID=$!

cd ..

echo ""
echo "🎉 AI-Learning is starting up!"
echo "=================================="
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "⚠️  Important: Make sure to add your OpenAI API key to backend/.env"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap 'echo ""; echo "🛑 Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

wait
