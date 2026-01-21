# TKR College Chatbot - Quick Start Script for Linux/Mac

echo "========================================"
echo "TKR College AI Chatbot - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/5] Checking Python installation..."
python3 --version
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "WARNING: MySQL command not found"
    echo "Make sure MySQL is installed and accessible"
    echo ""
fi

echo "[2/5] Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit backend/.env with your MySQL credentials!"
    echo "Press Enter after you've updated the .env file..."
    read
fi

echo "[3/5] Installing Python dependencies..."
echo "This may take a few minutes on first run..."
pip install -r requirements.txt --quiet

echo ""
echo "[4/5] Starting Flask backend server..."
echo "Backend will run on http://localhost:5000"
echo ""

# Start backend in background
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

echo "[5/5] Starting frontend server..."
cd ../frontend

# Start frontend in background
python3 -m http.server 8000 &
FRONTEND_PID=$!

# Wait a moment
sleep 3

echo ""
echo "========================================"
echo "TKR College Chatbot is now running!"
echo "========================================"
echo ""
echo "Backend API: http://localhost:5000"
echo "Frontend UI: http://localhost:8000"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop the servers, run:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Opening browser..."

# Try to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8000
elif command -v open &> /dev/null; then
    open http://localhost:8000
fi

echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait
