"""
Python ML Service - Flask API Server
Bridges the Node.js backend with the Python appointment agent and calendar service.
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from calendar_service import CalendarService
from appointment_agent import AppointmentAgent

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend/backend communication

# Global instances
calendar_service = None
appointment_agent = None

def initialize_services():
    """Initialize calendar service and appointment agent."""
    global calendar_service, appointment_agent
    
    try:
        # Initialize calendar service
        calendar_id = os.getenv('CALENDAR_ID', 'primary')
        timezone = os.getenv('TIMEZONE', 'America/New_York')
        calendar_service = CalendarService(
            calendar_id=calendar_id,
            timezone=timezone
        )
        print("✓ Calendar service initialized")
        print(f"  Calendar ID: {calendar_id}")
        print(f"  Timezone: {timezone}")
        
        # Initialize appointment agent
        doctor_name = os.getenv('DOCTOR_NAME', 'Dr. Smith')
        doctor_email = os.getenv('DOCTOR_EMAIL')
        appointment_agent = AppointmentAgent(
            calendar_service=calendar_service,
            doctor_name=doctor_name,
            doctor_email=doctor_email
        )
        print("✓ Appointment agent initialized")
        
        return True
    except Exception as e:
        print(f"Error initializing services: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'calendar_connected': calendar_service is not None,
        'agent_ready': appointment_agent is not None,
        'calendar_id': calendar_service.calendar_id if calendar_service else None
    })

@app.route('/check_auth', methods=['GET'])
def check_auth():
    """Check if Google Calendar authentication is configured."""
    try:
        if calendar_service is None:
            return jsonify({
                'success': False,
                'authenticated': False,
                'message': 'Calendar service not initialized'
            }), 500
        
        # Check if credentials file exists
        creds_exist = os.path.exists('credentials.json')
        token_exist = os.path.exists('token.pickle')
        
        return jsonify({
            'success': True,
            'authenticated': creds_exist and (token_exist or calendar_service.service is not None),
            'credentials_file': creds_exist,
            'token_file': token_exist,
            'calendar_id': calendar_service.calendar_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/set_credentials', methods=['POST'])
def set_credentials():
    """Set Google Calendar credentials (if needed for dynamic setup)."""
    try:
        # This endpoint can be used to set credentials dynamically
        # For now, we use the credentials.json file
        return jsonify({
            'success': True,
            'message': 'Credentials should be placed in credentials.json file'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend."""
    try:
        if appointment_agent is None:
            print("ERROR: Appointment agent is None")
            return jsonify({
                'success': False,
                'error': 'Appointment agent not initialized'
            }), 500
        
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400
        
        # Support both 'input' and 'message' keys
        user_message = data.get('input') or data.get('message', '')
        history = data.get('history', [])
        
        print(f"Received message: {user_message[:50]}...")
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get response from appointment agent
        try:
            response_text = appointment_agent.chat(user_message)
            print(f"Agent response generated: {len(response_text)} chars")
        except Exception as agent_error:
            print(f"Error in appointment agent: {agent_error}")
            raise agent_error
        
        # Check if appointment was confirmed
        should_transition = appointment_agent.extracted_info.get('confirmed', False)
        
        # Get event details if appointment was created
        event_info = None
        if should_transition and appointment_agent.extracted_info.get('confirmed'):
            # Try to get the last created event
            try:
                # Get recent events to find the one we just created
                from datetime import datetime, timedelta
                now = datetime.now(appointment_agent.calendar_service.timezone)
                events = appointment_agent.calendar_service.get_events(
                    now - timedelta(hours=1),
                    now + timedelta(days=30)
                )
                # Find the most recent event for this patient
                patient_name = appointment_agent.extracted_info.get('patient_name')
                if patient_name and events:
                    for event in reversed(events):
                        if patient_name in event.get('summary', ''):
                            event_info = {
                                'id': event.get('id'),
                                'htmlLink': event.get('htmlLink'),
                                'summary': event.get('summary'),
                                'start': event.get('start'),
                                'end': event.get('end')
                            }
                            break
            except Exception as e:
                print(f"Could not retrieve event info: {e}")
        
        return jsonify({
            'success': True,
            'response': response_text,
            'shouldTransition': should_transition,
            'extracted_info': {
                'patient_name': appointment_agent.extracted_info.get('patient_name'),
                'appointment_datetime': str(appointment_agent.extracted_info.get('appointment_datetime')) if appointment_agent.extracted_info.get('appointment_datetime') else None,
                'confirmed': appointment_agent.extracted_info.get('confirmed', False)
            },
            'event_info': event_info
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in chat endpoint: {e}")
        print(f"Traceback: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_trace if app.debug else None
        }), 500

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    """Book an appointment directly."""
    try:
        if calendar_service is None or appointment_agent is None:
            return jsonify({
                'success': False,
                'error': 'Services not initialized'
            }), 500
        
        data = request.json
        patient_name = data.get('patient_name')
        patient_email = data.get('patient_email')
        datetime_iso = data.get('datetime_iso')
        doctor_id = data.get('doctor_id')
        
        if not all([patient_name, datetime_iso]):
            return jsonify({
                'success': False,
                'error': 'patient_name and datetime_iso are required'
            }), 400
        
        # Parse datetime
        from datetime import datetime
        appointment_time = datetime.fromisoformat(datetime_iso.replace('Z', '+00:00'))
        
        # Create appointment
        event = calendar_service.create_appointment(
            patient_name=patient_name,
            appointment_time=appointment_time,
            doctor_name=os.getenv('DOCTOR_NAME', 'Dr. Smith'),
            doctor_email=os.getenv('DOCTOR_EMAIL')
        )
        
        return jsonify({
            'success': True,
            'booking': {
                'id': event.get('id'),
                'summary': event.get('summary'),
                'start': event.get('start'),
                'end': event.get('end'),
                'htmlLink': event.get('htmlLink'),
                'calendar_id': calendar_service.calendar_id
            }
        })
    except Exception as e:
        print(f"Error booking appointment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/list_events', methods=['GET'])
def list_events():
    """List recent events in the calendar for verification."""
    try:
        if calendar_service is None:
            return jsonify({
                'success': False,
                'error': 'Calendar service not initialized'
            }), 500
        
        from datetime import datetime, timedelta
        now = datetime.now(calendar_service.timezone)
        start_time = now - timedelta(days=7)
        end_time = now + timedelta(days=30)
        
        events = calendar_service.get_events(start_time, end_time)
        
        return jsonify({
            'success': True,
            'calendar_id': calendar_service.calendar_id,
            'events': [
                {
                    'id': e.get('id'),
                    'summary': e.get('summary'),
                    'start': e.get('start'),
                    'end': e.get('end'),
                    'htmlLink': e.get('htmlLink')
                }
                for e in events
            ],
            'count': len(events)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/reset', methods=['POST'])
def reset():
    """Reset the conversation."""
    try:
        if appointment_agent:
            appointment_agent.reset()
        return jsonify({
            'success': True,
            'message': 'Conversation reset'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  Python ML Service - Starting...")
    print("=" * 60)
    
    # Initialize services
    if not initialize_services():
        print("Failed to initialize services. Exiting.")
        sys.exit(1)
    
    port = int(os.getenv('ML_SERVICE_PORT', 5001))  # Changed from 5000 to avoid AirPlay conflict
    print(f"\n✓ ML Service running on http://localhost:{port}")
    print("  Available endpoints:")
    print("    GET  /health - Health check")
    print("    GET  /check_auth - Check authentication")
    print("    GET  /list_events - List recent calendar events")
    print("    POST /chat - Chat with AI agent")
    print("    POST /book_appointment - Book appointment")
    print("    POST /reset - Reset conversation")
    print("\n" + "=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
