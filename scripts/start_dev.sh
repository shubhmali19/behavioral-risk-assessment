#!/bin/bash
set -e
echo "Starting backend..."
cd "$(dirname "$0")/../backend"
DATABASE_URL=sqlite:///./risk_assessment.db uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

echo "Starting frontend..."
cd "$(dirname "$0")/../frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "System running:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
