# DocConnect - AI-Powered Doctor Appointment Booking System

DocConnect is an intelligent appointment booking system that uses AI to help patients schedule doctor appointments seamlessly. The system features an AI-powered chatbot that guides users through the booking process by collecting their information, understanding their symptoms, and automatically booking appointments with available doctors.

## 🌟 Features

- **AI-Powered Chat Assistant**: Uses Google Gemini to have natural conversations with patients
- **Smart Appointment Booking**: Automatically books appointments in Google Calendar
- **Symptom-Based Doctor Assignment**: Recommends appropriate doctors based on patient symptoms
- **Real-Time Availability Checking**: Checks doctor availability before booking
- **Multi-Platform Support**: Web interface with React frontend and Node.js backend
- **Google Calendar Integration**: Seamlessly integrates with Google Calendar API

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - For the ML service
- **Node.js 16+** - For backend and frontend
- **npm** - Node package manager
- **Google Cloud Account** - For API credentials
- **Git** - For version control

## 🚀 Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd DocConnect
```

### Step 2: Set Up Google Cloud Project

#### 2.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown and select "NEW PROJECT"
3. Enter project name: "DocConnect"
4. Click "CREATE"

#### 2.2 Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for and enable the following APIs:
   - **Google Calendar API**
   - **Google Generative Language API** (for Gemini)

#### 2.3 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **"Create Credentials"** > **"OAuth client ID"**
3. Choose **"Desktop app"** as the application type
4. Click **"Create"**
5. Download the JSON file and save it as `credentials.json` in the project root

#### 2.4 Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **"External"** as the user type
3. Fill in the required information:
   - App name: "DocConnect"
   - User support email: Your email
   - Developer contact: Your email
4. Click **"Save and Continue"**
5. Add the following scopes:
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/generativelanguage.readonly`
6. Add your email as a test user
7. Click **"Save and Continue"** and then **"Back to Dashboard"**

### Step 3: Get Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click **"Create API Key"**
3. Copy the API key

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Google API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Calendar Configuration
CALENDAR_ID=primary
TIMEZONE=Asia/Kolkata

# Doctor Configuration
DOCTOR_NAME=Dr. Pavan Kumar
DOCTOR_EMAIL=your_doctor_email@example.com

# Backend Configuration
BACKEND_PORT=5000
ML_SERVICE_PORT=5001

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
```

### Step 5: Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Install Node.js Dependencies

```bash
# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install
```

### Step 7: Verify Google Calendar API Setup

Run the authentication check:

```bash
python test_setup.py
```

This will:
- Test Google Calendar API connection
- Test Google Gemini API connection
- Create necessary authentication tokens

## 🎯 Running the Application

### Option 1: Start All Services Individually

#### Terminal 1 - Start Python ML Service
```bash
python ml_service.py
```
The ML service will run on `http://localhost:5001`

#### Terminal 2 - Start Node.js Backend
```bash
cd backend
npm start
```
The backend will run on `http://localhost:5000`

#### Terminal 3 - Start React Frontend
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:5173` (or the port shown in terminal)

### Option 2: Use the Start Script

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
```

Make it executable and run:
```bash
chmod +x start_all.sh
./start_all.sh
```

## 📱 Using the Application

### Conversation Flow

1. **Greeting**: The AI assistant greets you and asks for your name
2. **Symptoms**: Describe your symptoms or reason for the visit
3. **Doctor Assignment**: The AI recommends Dr. Pavan Kumar based on your symptoms
4. **Date & Time**: Specify your preferred appointment date and time
5. **Confirmation**: Review and confirm your appointment details
6. **Booking**: The appointment is automatically added to Google Calendar

### Example Conversation

```
You: Hello
Agent: Welcome to HealthConnect! I'm here to help you book an appointment with Dr. Pavan Kumar. 
       May I have your name please?

You: My name is John Smith
Agent: Nice to meet you, John! Could you please describe your symptoms or reason for the visit?

You: I have been having headaches and fever for the past 2 days
Agent: Thank you for sharing that, John. Based on your symptoms, Dr. Pavan Kumar is the perfect 
       specialist for your condition. When would you like to schedule your appointment? 
       Please provide a date and time (e.g., "today at 2 PM" or "tomorrow at 10 AM").

You: Today at 1 PM
Agent: ✅ Appointment confirmed!
       Patient: John Smith
       Date & Time: Wednesday, November 19, 2025 at 1:00 PM
       Doctor: Dr. Pavan Kumar
       
       Your appointment has been successfully added to your Google Calendar.
```

## 🔧 API Endpoints

### ML Service (Python Flask)
- `GET /health` - Health check
- `GET /check_auth` - Check authentication status
- `GET /list_events` - List recent calendar events
- `POST /chat` - Chat with AI agent
- `POST /book_appointment` - Book appointment
- `POST /reset` - Reset conversation

### Backend (Node.js Express)
- `GET /api/health` - Health check
- `GET /api/doctors` - Get list of doctors
- `POST /api/book` - Book appointment
- `GET /api/appointments` - Get user appointments

## 📁 Project Structure

```
DocConnect/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── credentials.json          # Google OAuth credentials (not in repo)
├── token.pickle             # Google OAuth token (auto-generated)
├── main.py                  # CLI entry point
├── ml_service.py            # Flask ML service
├── calendar_service.py      # Google Calendar API wrapper
├── appointment_agent.py     # AI appointment booking agent
├── test_setup.py            # Setup verification script
├── backend/                 # Node.js backend
│   ├── package.json
│   ├── server.js
│   └── routes/
├── frontend/                # React frontend
│   ├── package.json
│   ├── src/
│   ├── public/
│   └── vite.config.js
└── docs/                    # Documentation
    ├── ENABLE_CALENDAR_API.md
    ├── ENABLE_GEMINI_API.md
    └── START_SERVERS.md
```

## 🐛 Troubleshooting

### Issue: "API has not been used in project"

**Solution**: Enable the required APIs in Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** > **Library**
3. Search for "Google Calendar API" and click **Enable**
4. Search for "Google Generative Language API" and click **Enable**
5. Wait 1-2 minutes for changes to propagate

### Issue: "Invalid credentials file"

**Solution**: Ensure you have the correct credentials:
1. Delete the existing `credentials.json` file
2. Go to [Google Cloud Console](https://console.cloud.google.com/)
3. Create new OAuth 2.0 credentials for "Desktop app"
4. Download and save as `credentials.json` in the project root

### Issue: "Token has been expired or revoked"

**Solution**: Delete the token file and re-authenticate:
```bash
rm token.pickle
python ml_service.py
```

### Issue: Calendar ID not found (404 error)

**Solution**: Use 'primary' as the calendar ID or get the correct calendar ID:
1. Go to [Google Calendar Settings](https://calendar.google.com/calendar/u/0/r/settings)
2. Find your calendar and copy the Calendar ID
3. Update `CALENDAR_ID` in your `.env` file

### Issue: Port already in use

**Solution**: Change the port in the configuration or kill the process using the port:
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>
```

## 📚 Documentation

For more detailed information, see:
- [Enable Calendar API](./docs/ENABLE_CALENDAR_API.md)
- [Enable Gemini API](./docs/ENABLE_GEMINI_API.md)
- [Start Servers Guide](./docs/START_SERVERS.md)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the documentation in the `docs/` folder
3. Check existing GitHub issues
4. Create a new issue with detailed information

## 🎉 Acknowledgments

- Google Calendar API for appointment management
- Google Gemini AI for natural language processing
- React for the frontend framework
- Express.js for the backend framework
- LangChain for AI integration

---

**Happy booking! 🏥**

