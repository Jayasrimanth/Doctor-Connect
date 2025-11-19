"""
Google Calendar Service for managing appointments.
Handles OAuth authentication, calendar operations, and appointment management.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz


class CalendarService:
    """Service for interacting with Google Calendar API."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = 'credentials.json', 
                 token_file: str = 'token.pickle',
                 calendar_id: str = 'primary',
                 timezone: str = 'America/New_York'):
        """
        Initialize the Calendar Service.
        
        Args:
            credentials_file: Path to Google OAuth credentials JSON file
            token_file: Path to store OAuth token
            calendar_id: Google Calendar ID to use
            timezone: Timezone for appointments
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.calendar_id = calendar_id
        self.timezone = pytz.timezone(timezone)
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API using OAuth."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"Warning: Could not load existing token: {e}")
                creds = None
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Could not refresh token: {e}")
                    creds = None
            
            if not creds or not creds.valid:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                # Validate credentials file format
                try:
                    import json
                    with open(self.credentials_file, 'r') as f:
                        creds_data = json.load(f)
                    
                    # Check if it's the correct format for installed app
                    if 'installed' not in creds_data and 'web' not in creds_data:
                        raise ValueError(
                            "Invalid credentials file format. The file must contain either "
                            "'installed' (for Desktop app) or 'web' (for Web app) key.\n"
                            "Please ensure you downloaded the correct OAuth 2.0 Client ID "
                            "credentials from Google Cloud Console.\n"
                            "For Desktop app, choose 'Desktop app' as the application type."
                        )
                    
                    # If it's a web app, provide helpful message
                    if 'web' in creds_data and 'installed' not in creds_data:
                        raise ValueError(
                            "The credentials file is for a 'Web application', but this app "
                            "requires 'Desktop app' credentials.\n"
                            "Please create new OAuth 2.0 credentials in Google Cloud Console:\n"
                            "1. Go to APIs & Services > Credentials\n"
                            "2. Click 'Create Credentials' > 'OAuth client ID'\n"
                            "3. Choose 'Desktop app' as the application type\n"
                            "4. Download the new credentials file"
                        )
                except json.JSONDecodeError:
                    raise ValueError(
                        f"Invalid JSON in credentials file '{self.credentials_file}'. "
                        "Please ensure the file is a valid JSON file downloaded from "
                        "Google Cloud Console."
                    )
                except Exception as e:
                    if isinstance(e, (ValueError, FileNotFoundError)):
                        raise
                    # If validation fails for other reasons, continue anyway
                    pass
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except ValueError as e:
                    if "Client secrets must be for a web or installed app" in str(e):
                        raise ValueError(
                            "Invalid credentials file format.\n\n"
                            "The credentials.json file must be for a 'Desktop app' (installed app).\n\n"
                            "To fix this:\n"
                            "1. Go to https://console.cloud.google.com/\n"
                            "2. Navigate to APIs & Services > Credentials\n"
                            "3. Click 'Create Credentials' > 'OAuth client ID'\n"
                            "4. IMPORTANT: Select 'Desktop app' as the application type\n"
                            "5. Click 'Create' and download the JSON file\n"
                            "6. Replace your current credentials.json with the new file\n\n"
                            f"Current file location: {os.path.abspath(self.credentials_file)}"
                        ) from e
                    raise
            
            # Save credentials for future use
            if creds:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_available_slots(self, date: datetime, duration_minutes: int = 30,
                           start_hour: int = 9, end_hour: int = 17) -> List[datetime]:
        """
        Get available time slots for a given date.
        
        Args:
            date: Date to check availability
            duration_minutes: Duration of each appointment slot
            start_hour: Start hour (24-hour format)
            end_hour: End hour (24-hour format)
        
        Returns:
            List of available datetime slots
        """
        # Get existing events for the date
        start_of_day = self.timezone.localize(
            datetime.combine(date.date(), datetime.min.time().replace(hour=start_hour))
        )
        end_of_day = self.timezone.localize(
            datetime.combine(date.date(), datetime.min.time().replace(hour=end_hour))
        )
        
        existing_events = self.get_events(start_of_day, end_of_day)
        
        # Generate all possible slots
        slots = []
        current = start_of_day
        while current < end_of_day:
            slots.append(current)
            current += timedelta(minutes=duration_minutes)
        
        # Filter out occupied slots
        available_slots = []
        for slot in slots:
            slot_end = slot + timedelta(minutes=duration_minutes)
            is_available = True
            
            for event in existing_events:
                event_start = self._parse_datetime(event['start'])
                event_end = self._parse_datetime(event['end'])
                
                # Check for overlap
                if not (slot_end <= event_start or slot >= event_end):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(slot)
        
        return available_slots
    
    def get_events(self, time_min: datetime, time_max: datetime) -> List[Dict[str, Any]]:
        """
        Get events from calendar within a time range.
        
        Args:
            time_min: Start time
            time_max: End time
        
        Returns:
            List of event dictionaries
        """
        try:
            time_min_str = time_min.isoformat()
            time_max_str = time_max.isoformat()
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def create_appointment(self, patient_name: str, appointment_time: datetime,
                          duration_minutes: int = 30, doctor_name: str = "Dr. Smith",
                          doctor_email: str = None, notes: str = None) -> Dict[str, Any]:
        """
        Create an appointment in Google Calendar.
        
        Args:
            patient_name: Name of the patient
            appointment_time: Datetime for the appointment
            duration_minutes: Duration of the appointment
            doctor_name: Name of the doctor
            doctor_email: Email of the doctor
            notes: Additional notes for the appointment
        
        Returns:
            Created event dictionary
        """
        # Ensure appointment_time is timezone-aware
        if appointment_time.tzinfo is None:
            appointment_time = self.timezone.localize(appointment_time)
        
        end_time = appointment_time + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': f'Appointment: {patient_name}',
            'description': f'Patient: {patient_name}\nDoctor: {doctor_name}',
            'start': {
                'dateTime': appointment_time.isoformat(),
                'timeZone': str(self.timezone),
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': str(self.timezone),
            },
        }
        
        if notes:
            event['description'] += f'\nNotes: {notes}'
        
        if doctor_email:
            event['attendees'] = [
                {'email': doctor_email}
            ]
        
        try:
            print(f"Creating appointment in calendar: {self.calendar_id}")
            print(f"Event details: {patient_name} at {appointment_time}")
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            print(f"✅ Event created successfully!")
            print(f"   Event ID: {created_event.get('id')}")
            print(f"   Event Link: {created_event.get('htmlLink', 'N/A')}")
            print(f"   Calendar: {self.calendar_id}")
            
            return created_event
        except HttpError as error:
            error_details = error.error_details if hasattr(error, 'error_details') else []
            error_message = str(error)
            
            # Check for API not enabled error
            if 'accessNotConfigured' in str(error) or 'API has not been used' in str(error):
                raise Exception(
                    f"Google Calendar API is not enabled in your project.\n\n"
                    f"🔧 SOLUTION:\n"
                    f"1. Go to: https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview\n"
                    f"2. Select your project\n"
                    f"3. Click 'Enable' button\n"
                    f"4. Wait 1-2 minutes for changes to propagate\n"
                    f"5. Try again\n\n"
                    f"See ENABLE_CALENDAR_API.md for detailed instructions."
                )
            
            raise Exception(f"Failed to create appointment: {error}")
    
    def check_conflict(self, appointment_time: datetime, duration_minutes: int = 30) -> bool:
        """
        Check if an appointment time conflicts with existing events.
        
        Args:
            appointment_time: Proposed appointment time
            duration_minutes: Duration of the appointment
        
        Returns:
            True if there's a conflict, False otherwise
        """
        if appointment_time.tzinfo is None:
            appointment_time = self.timezone.localize(appointment_time)
        
        end_time = appointment_time + timedelta(minutes=duration_minutes)
        events = self.get_events(appointment_time, end_time)
        
        return len(events) > 0
    
    def _parse_datetime(self, dt_dict: Dict[str, str]) -> datetime:
        """Parse datetime from Google Calendar event format."""
        if 'dateTime' in dt_dict:
            dt = datetime.fromisoformat(dt_dict['dateTime'].replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(dt_dict['date'] + 'T00:00:00')
        
        if dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        
        return dt
    
    def suggest_next_available(self, preferred_date: datetime, 
                              duration_minutes: int = 30,
                              max_days_ahead: int = 30) -> Optional[datetime]:
        """
        Suggest the next available appointment slot.
        
        Args:
            preferred_date: Preferred date/time
            duration_minutes: Duration of appointment
            max_days_ahead: Maximum days to look ahead
        
        Returns:
            Next available datetime or None if none found
        """
        current_date = preferred_date
        end_date = current_date + timedelta(days=max_days_ahead)
        
        while current_date <= end_date:
            slots = self.get_available_slots(current_date, duration_minutes)
            if slots:
                # Return the first available slot on or after preferred time
                for slot in slots:
                    if slot >= preferred_date:
                        return slot
                # If no slot after preferred time, return first slot of next day
                if current_date < end_date:
                    current_date = current_date + timedelta(days=1)
                    current_date = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
                    continue
            current_date = current_date + timedelta(days=1)
            current_date = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return None


