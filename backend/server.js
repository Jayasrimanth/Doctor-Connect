/**
 * Node.js API Gateway & Orchestrator
 * 
 * This server acts as a proxy between the React frontend and the Python ML Service.
 * It handles Google Calendar authentication and serves doctor data.
 * 
 * Installation:
 * npm install express cors axios dotenv
 * 
 * Usage:
 * node server.js
 */

const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:5001';  // Changed from 5000 to avoid AirPlay conflict

app.use(cors());
app.use(express.json());

// Mock doctor data
const doctors = [
  {
    id: "1",
    name: "Dr. Elena Martinez",
    specialization: "Internal Medicine",
    experience: 15,
    image_url: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop",
    email: "elena.martinez@healthconnect.com"
  },
  {
    id: "2",
    name: "Dr. James Wilson",
    specialization: "General Practitioner",
    experience: 12,
    image_url: "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop",
    email: "james.wilson@healthconnect.com"
  },
  {
    id: "3",
    name: "Dr. Sarah Chen",
    specialization: "Pediatrics",
    experience: 10,
    image_url: "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=400&h=400&fit=crop",
    email: "sarah.chen@healthconnect.com"
  },
  {
    id: "4",
    name: "Dr. Michael Brown",
    specialization: "Cardiology",
    experience: 18,
    image_url: "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&h=400&fit=crop",
    email: "michael.brown@healthconnect.com"
  },
  {
    id: "5",
    name: "Dr. Lisa Anderson",
    specialization: "Dermatology",
    experience: 14,
    image_url: "https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=400&h=400&fit=crop",
    email: "lisa.anderson@healthconnect.com"
  },
  {
    id: "6",
    name: "Dr. David Kim",
    specialization: "Orthopedics",
    experience: 16,
    image_url: "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&h=400&fit=crop",
    email: "david.kim@healthconnect.com"
  }
];

/**
 * POST /api/init_auth
 * 
 * Receives Google Calendar credentials and forwards them to the ML Service.
 * This should be called once during deployment/setup with the clinic's credentials.
 */
app.post('/api/init_auth', async (req, res) => {
  try {
    const credentials = req.body;
    
    // Forward credentials to Python ML Service
    const response = await axios.post(`${ML_SERVICE_URL}/set_credentials`, credentials);
    
    res.json({
      success: true,
      message: 'Credentials successfully set',
      mlServiceResponse: response.data
    });
  } catch (error) {
    console.error('Error setting credentials:', error.message);
    res.status(500).json({
      success: false,
      error: 'Failed to set credentials',
      details: error.message
    });
  }
});

/**
 * GET /api/doctors
 * 
 * Returns the list of available doctors with their details.
 */
app.get('/api/doctors', (req, res) => {
  res.json({
    success: true,
    doctors: doctors
  });
});

/**
 * POST /api/chat
 * 
 * Proxies chat messages to the Python ML Service and returns the AI response.
 */
app.post('/api/chat', async (req, res) => {
  try {
    const { message, history } = req.body;
    
    console.log('Backend received chat request:', { message: message?.substring(0, 50), hasHistory: !!history });
    
    if (!message) {
      return res.status(400).json({
        success: false,
        error: 'Message is required'
      });
    }
    
    // Forward to Python ML Service
    console.log(`Forwarding to ML service: ${ML_SERVICE_URL}/chat`);
    const response = await axios.post(`${ML_SERVICE_URL}/chat`, {
      input: message,
      message: message,  // Send both for compatibility
      history: history || []
    }, {
      timeout: 30000  // 30 second timeout
    });
    
    console.log('ML service response received:', response.data.success ? 'success' : 'failed');
    
    res.json({
      success: true,
      response: response.data.response,
      shouldTransition: response.data.shouldTransition || false
    });
  } catch (error) {
    console.error('Error in chat:', error.message);
    console.error('Error details:', error.response?.data || error.message);
    
    // Provide more detailed error information
    const errorMessage = error.response?.data?.error || error.message || 'Failed to process chat message';
    const errorDetails = error.response?.data?.details || error.message;
    
    res.status(error.response?.status || 500).json({
      success: false,
      error: errorMessage,
      details: errorDetails,
      mlServiceUrl: ML_SERVICE_URL
    });
  }
});

/**
 * GET /api/check_auth
 * 
 * Checks if Google Calendar credentials have been configured.
 */
app.get('/api/check_auth', async (req, res) => {
  try {
    const response = await axios.get(`${ML_SERVICE_URL}/check_auth`);
    res.json(response.data);
  } catch (error) {
    console.error('Error checking auth:', error.message);
    res.status(500).json({
      success: false,
      error: 'Failed to check authentication status',
      details: error.message
    });
  }
});

/**
 * POST /api/book
 * 
 * Optional endpoint for direct booking if not handled through chat.
 */
app.post('/api/book', async (req, res) => {
  try {
    const { doctorId, patientName, patientEmail, datetime } = req.body;
    
    // Forward to Python ML Service
    const response = await axios.post(`${ML_SERVICE_URL}/book_appointment`, {
      doctor_id: doctorId,
      patient_name: patientName,
      patient_email: patientEmail,
      datetime_iso: datetime
    });
    
    res.json({
      success: true,
      booking: response.data
    });
  } catch (error) {
    console.error('Error booking appointment:', error.message);
    res.status(500).json({
      success: false,
      error: 'Failed to book appointment',
      details: error.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`Node.js API Gateway running on port ${PORT}`);
  console.log(`ML Service URL: ${ML_SERVICE_URL}`);
  console.log('\nAvailable endpoints:');
  console.log('  POST /api/init_auth - Initialize Google Calendar credentials');
  console.log('  GET  /api/doctors - Get list of doctors');
  console.log('  POST /api/chat - Send chat message to AI');
  console.log('  GET  /api/check_auth - Check authentication status');
  console.log('  POST /api/book - Book appointment directly');
});

module.exports = app;
