# How to Start All Services

This guide shows you how to run the complete application with frontend, backend, and Python ML service.

## Architecture

```
Frontend (React) → Backend (Node.js) → ML Service (Python Flask) → Google Calendar
     :8080              :3001                  :5000
```

## Prerequisites

1. ✅ Python 3.8+ with all packages installed
2. ✅ Node.js and npm installed
3. ✅ Google Calendar credentials.json in project root
4. ✅ .env file with GEMINI_API_KEY

## Step-by-Step Startup

### Terminal 1: Python ML Service

```bash
cd /Users/vaddi/Desktop/Projects/DocConnect
python ml_service.py
```

**Expected output:**
```
✓ Calendar service initialized
✓ Appointment agent initialized
✓ ML Service running on http://localhost:5000
```

### Terminal 2: Node.js Backend

```bash
cd /Users/vaddi/Desktop/Projects/DocConnect/backend
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

**Expected output:**
```
Node.js API Gateway running on port 3001
ML Service URL: http://localhost:5001
```

### Terminal 3: React Frontend

```bash
cd /Users/vaddi/Desktop/Projects/DocConnect/frontend
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:8080/
  ➜  Network: use --host to expose
```

## Quick Start Script

Create a file `start_all.sh`:

```bash
#!/bin/bash

# Start Python ML Service
echo "Starting Python ML Service..."
cd /Users/vaddi/Desktop/Projects/DocConnect
python ml_service.py &
ML_PID=$!

# Wait a bit for ML service to start
sleep 3

# Start Node.js Backend
echo "Starting Node.js Backend..."
cd /Users/vaddi/Desktop/Projects/DocConnect/backend
npm start &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start React Frontend
echo "Starting React Frontend..."
cd /Users/vaddi/Desktop/Projects/DocConnect/frontend
npm run dev &
FRONTEND_PID=$!

echo "All services started!"
echo "ML Service PID: $ML_PID"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
```

Make it executable:
```bash
chmod +x start_all.sh
```

## Verify Services

1. **ML Service**: http://localhost:5001/health
   - Should return: `{"status":"healthy"}`

2. **Backend**: http://localhost:3001/api/doctors
   - Should return: `{"success":true,"doctors":[...]}`

3. **Frontend**: http://localhost:8080
   - Should show the HealthConnect dashboard

## Troubleshooting

### "Port already in use"
- Kill the process using the port:
  ```bash
  # For port 5001 (ML Service)
  lsof -ti:5001 | xargs kill -9
  
  # For port 3001 (Backend)
  lsof -ti:3001 | xargs kill -9
  
  # For port 8080 (Frontend)
  lsof -ti:8080 | xargs kill -9
  ```

### "Module not found" errors
- **Python**: Run `pip install -r requirements.txt`
- **Node.js Backend**: Run `cd backend && npm install`
- **React Frontend**: Run `cd frontend && npm install`

### "Cannot connect to ML Service"
- Make sure Python ML service is running on port 5001
- Check that `ML_SERVICE_URL` in backend/.env is correct (should be http://localhost:5001)

### "API calls failing"
- Check browser console for CORS errors
- Verify all three services are running
- Check network tab for failed requests

## Environment Variables

### Root .env (for Python services)
```env
GEMINI_API_KEY=your-key-here
CALENDAR_ID=primary
TIMEZONE=America/New_York
DOCTOR_NAME=Dr. Smith
DOCTOR_EMAIL=doctor@example.com
ML_SERVICE_PORT=5001
```

### backend/.env (optional)
```env
PORT=3001
ML_SERVICE_URL=http://localhost:5001
```

### frontend/.env (optional)
```env
VITE_API_URL=http://localhost:3001
```

## Development Tips

1. **Auto-reload**: Use `npm run dev` in backend for auto-reload
2. **Hot reload**: Frontend has hot reload by default with Vite
3. **Debugging**: Check browser console and terminal outputs
4. **Logs**: All services print useful debug information

## Production Deployment

For production, you'll need to:
1. Build the frontend: `cd frontend && npm run build`
2. Use a process manager (PM2, systemd, etc.)
3. Set up reverse proxy (nginx)
4. Configure environment variables securely
5. Use HTTPS

---

**All services are now connected and ready to use!** 🚀

