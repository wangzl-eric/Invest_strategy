description: "Start backend and frontend servers for development"

# Start backend server (port 8000) in background
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy/backend"
echo "Starting backend on http://localhost:8000 (API docs at /docs)..."
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 3

# Start frontend server (port 8050) in background
cd "/Users/zelin/Desktop/PA Investment/Invest_strategy/frontend"
echo "Starting frontend on http://localhost:8050..."
python app.py &

echo ""
echo "=== Servers Started ==="
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Frontend: http://localhost:8050"
echo ""
echo "To stop servers, run: pkill -f 'uvicorn\|app.py'"
