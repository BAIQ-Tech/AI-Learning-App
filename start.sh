#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting AI-Learning Application"
echo "=================================="

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the AI-Learning root directory"
    exit 1
fi

# Default values
ENV_FILE=".env"
PORT=8000
HOST="0.0.0.0"
WORKERS=4
LOG_LEVEL="info"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENV_FILE="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --env FILE       Path to environment file (default: .env)"
            echo "  --port PORT      Port to run the server on (default: 8000)"
            echo "  --host HOST      Host to bind to (default: 0.0.0.0)"
            echo "  --workers N      Number of worker processes (default: 4)"
            echo "  --log-level LVL  Log level (default: info)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Load environment variables if .env file exists
if [ -f "$ENV_FILE" ]; then
    echo "🔧 Loading environment variables from $ENV_FILE"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "⚠️  No .env file found. Using system environment variables."
fi

# Set default environment variables if not set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

# Check for required commands
REQUIRED_COMMANDS=("python3" "pip3")
for cmd in "${REQUIRED_COMMANDS[@]}"; do
    if ! command_exists "$cmd"; then
        echo "❌ Error: $cmd is not installed. Please install it first."
        exit 1
    fi
done

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "❌ Error: Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -e .

# Check if we should start the backend
if [ "$1" != "--frontend-only" ]; then
    echo "🚀 Starting Backend Service..."
    echo "   Host: $HOST"
    echo "   Port: $PORT"
    echo "   Workers: $WORKERS"
    echo "   Log Level: $LOG_LEVEL"
    
    # Run database migrations if needed
    if [ -f "alembic.ini" ]; then
        echo "🔄 Running database migrations..."
        alembic upgrade head
    fi
    
    # Start the FastAPI application with Gunicorn
    gunicorn \
        --bind "$HOST:$PORT" \
        --workers "$WORKERS" \
        --worker-class uvicorn.workers.UvicornWorker \
        --log-level "$LOG_LEVEL" \
        --pythonpath "$(pwd)" \
        main:app &
    BACKEND_PID=$!
    
    echo "✅ Backend service started with PID $BACKEND_PID"
    echo "   API available at http://$HOST:$PORT"
    echo "   API docs available at http://$HOST:$PORT/docs"
else
    echo "Skipping backend startup (--frontend-only flag detected)"
fi

# Check if we should start the frontend
if [ "$1" != "--backend-only" ]; then
    echo ""
    echo "🌐 Setting up frontend..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        if [ ! -d "node_modules" ]; then
            echo "📦 Installing frontend dependencies..."
            if ! npm install; then
                echo "❌ Failed to install frontend dependencies"
                exit 1
            fi
        fi
        
        echo "🚀 Starting frontend development server..."
        npm run dev &
        FRONTEND_PID=$!
        echo "✅ Frontend started with PID $FRONTEND_PID"
        echo "   Development server available at http://localhost:3000"
    else
        echo "⚠️  Frontend directory not found. Skipping frontend startup."
    fi
else
    echo "Skipping frontend startup (--backend-only flag detected)"
fi

# Wait for all background processes to complete
wait
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
