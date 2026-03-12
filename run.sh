#!/bin/bash

# Define cleanup function to kill background processes on exit
cleanup() {
    echo -e "\n🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "🚀 Starting AI Chatbot Portfolio..."

# Start the Backend Server
echo "➡️ Starting FastApi Backend on Port 8000..."
cd backend || exit
# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start the Frontend Server using Python's built-in simple HTTP server
echo "➡️ Starting Frontend Web Server on Port 3000..."
cd frontend || exit
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo -e "\n✅ All systems go!"
echo "--------------------------------------------------------"
echo "🌐 Frontend URL: http://localhost:3000"
echo "⚙️  Backend API:  http://localhost:8000"
echo "--------------------------------------------------------"
echo "Press Ctrl+C to stop both servers gracefully."

# Wait indefinitely so the script doesn't exit immediately
wait
