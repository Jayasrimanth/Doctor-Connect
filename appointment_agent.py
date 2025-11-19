"""
AI-powered conversational agent for doctor appointment booking.
Uses LangChain and Google Gemini to handle natural language conversations.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from langchain.memory import ConversationBufferMemory
except ImportError:
    raise ImportError(
        "langchain-google-genai package not found. "
        "Install it with: pip install langchain-google-genai"
    )
from calendar_service import CalendarService
import re
import pytz


load_dotenv()


class AppointmentAgent:
    """AI agent for booking doctor appointments."""
    
    def __init__(self, calendar_service: CalendarService,
                 doctor_name: str = "Dr. Smith",
                 doctor_email: str = None):
        """
        Initialize the appointment booking agent.
        
        Args:
            calendar_service: CalendarService instance
            doctor_name: Name of the doctor
            doctor_email: Email of the doctor
        """
        self.calendar_service = calendar_service
        self.doctor_name = doctor_name
        self.doctor_email = doctor_email
        
        # Initialize Google Gemini LLM
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Please add GEMINI_API_KEY to your .env file. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Use Gemini model - try different model names based on availability
        # Common model names: gemini-1.5-flash, gemini-1.5-pro, gemini-pro
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        
        # List of models to try in order
        models_to_try = [
            model_name,  # Try user-specified first
            'gemini-2.5-flash',  # Fast and free
            'gemini-2.5-pro',    # Better quality
            'gemini-pro',        # Legacy
        ]
        
        # Remove duplicates while preserving order
        models_to_try = list(dict.fromkeys(models_to_try))
        
        self.llm = None
        last_error = None
        
        for model in models_to_try:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=model,
                    temperature=0.7,
                    google_api_key=api_key
                )
                # Try a simple test to verify the model works
                test_response = self.llm.invoke([HumanMessage(content="Hi")])
                if test_response and hasattr(test_response, 'content'):
                    print(f"✓ Using Gemini model: {model}")
                    break
            except Exception as e:
                last_error = e
                if model != models_to_try[-1]:  # Don't print error for last attempt
                    print(f"⚠️  Model '{model}' not available, trying next...")
                continue
        
        if self.llm is None:
            error_msg = str(last_error) if last_error else "Unknown error"
            raise ValueError(
                f"\n❌ Could not initialize any Gemini model.\n"
                f"Error: {error_msg}\n\n"
                "🔧 SOLUTION: Enable Generative Language API\n\n"
                "1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com\n"
                "2. Select your project (same one used for Calendar API)\n"
                "3. Click 'Enable' button\n"
                "4. Wait 10-30 seconds for it to enable\n"
                "5. Run the application again\n\n"
                "📖 See ENABLE_GEMINI_API.md for detailed instructions.\n"
            )
        
        # Conversation memory - using simple list for compatibility
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Extract information during conversation
        self.extracted_info = {
            'patient_name': None,
            'symptoms': None,
            'preferred_date': None,
            'preferred_time': None,
            'appointment_datetime': None,
            'doctor_assigned': False,
            'confirmed': False
        }
        
        # Conversation stage tracking
        self.conversation_stage = 'greeting'  # greeting -> name -> symptoms -> datetime -> confirmation -> completed
        
        # System prompt
        self.system_prompt = f"""You are a friendly and professional AI assistant helping patients book appointments with {doctor_name}. 

Your role is to:
1. Greet the patient warmly
2. Collect the patient's name
3. Ask about their symptoms or reason for visit
4. Based on symptoms, recommend {doctor_name} as the best match
5. Ask for their preferred date and time for the appointment
6. Check availability and suggest alternatives if needed
7. Confirm the appointment details before booking
8. Be helpful, patient, and clear in your communication

Guidelines:
- Always be polite and professional
- If a requested time is not available, suggest the next available slot
- Always confirm appointment details before finalizing
- Use natural, conversational language
- If the user provides incomplete information, ask clarifying questions
- Format dates and times clearly (e.g., "Monday, January 15th at 2:00 PM")
- After collecting symptoms, always recommend {doctor_name} as the specialist for their condition

Current date and time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
"""
        
        # Initialize conversation
        self._initialize_conversation()
    
    def _initialize_conversation(self):
        """Initialize the conversation with system message."""
        self.memory.chat_memory.add_message(
            SystemMessage(content=self.system_prompt)
        )
    
    def _extract_patient_name(self, message: str) -> Optional[str]:
        """Extract patient name from user message."""
        # Simple extraction - can be enhanced
        patterns = [
            r"(?:my name is|i'm|i am|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_symptoms(self, message: str) -> Optional[str]:
        """Extract symptoms from user message."""
        # If message is long enough and doesn't look like a name or date, treat it as symptoms
        if len(message) > 10 and not re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', message):
            return message.strip()
        return None
    
    def _parse_datetime(self, message: str) -> Optional[datetime]:
        """Parse date and time from natural language."""
        message_lower = message.lower()
        now = datetime.now()
        tz = self.calendar_service.timezone
        
        # Try to extract date and time
        date_patterns = [
            (r'today', now),
            (r'tomorrow', now + timedelta(days=1)),
            (r'monday|mon', self._next_weekday(now, 0)),
            (r'tuesday|tue', self._next_weekday(now, 1)),
            (r'wednesday|wed', self._next_weekday(now, 2)),
            (r'thursday|thu', self._next_weekday(now, 3)),
            (r'friday|fri', self._next_weekday(now, 4)),
            (r'saturday|sat', self._next_weekday(now, 5)),
            (r'sunday|sun', self._next_weekday(now, 6)),
        ]
        
        parsed_date = None
        for pattern, date in date_patterns:
            if re.search(pattern, message_lower):
                parsed_date = date
                break
        
        # Extract time
        time_patterns = [
            (r'(\d{1,2}):(\d{2})\s*(am|pm)', self._parse_12h_time),
            (r'(\d{1,2})\s*(am|pm)', self._parse_12h_time_simple),
            (r'(\d{1,2}):(\d{2})', self._parse_24h_time),
        ]
        
        parsed_time = None
        for pattern, parser in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                parsed_time = parser(match)
                break
        
        if parsed_date and parsed_time:
            # Combine date and time
            appointment_dt = parsed_date.replace(
                hour=parsed_time.hour,
                minute=parsed_time.minute,
                second=0,
                microsecond=0
            )
            return tz.localize(appointment_dt)
        elif parsed_date:
            # Just date, use default time (9 AM)
            appointment_dt = parsed_date.replace(hour=9, minute=0, second=0, microsecond=0)
            return tz.localize(appointment_dt)
        
        return None
    
    def _next_weekday(self, d: datetime, weekday: int) -> datetime:
        """Get next occurrence of a weekday."""
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + timedelta(days=days_ahead)
    
    def _parse_12h_time(self, match) -> datetime:
        """Parse 12-hour time format."""
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        period = match.group(3).lower()
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        
        return datetime(1900, 1, 1, hour, minute)
    
    def _parse_12h_time_simple(self, match) -> datetime:
        """Parse simple 12-hour time format."""
        hour = int(match.group(1))
        period = match.group(2).lower()
        
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        
        return datetime(1900, 1, 1, hour, 0)
    
    def _parse_24h_time(self, match) -> datetime:
        """Parse 24-hour time format."""
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        return datetime(1900, 1, 1, hour, minute)
    
    def _update_extracted_info(self, message: str):
        """Update extracted information from user message."""
        # Extract patient name
        if not self.extracted_info['patient_name']:
            name = self._extract_patient_name(message)
            if name:
                self.extracted_info['patient_name'] = name
                self.conversation_stage = 'symptoms'
        
        # Extract symptoms
        if self.extracted_info['patient_name'] and not self.extracted_info['symptoms']:
            symptoms = self._extract_symptoms(message)
            if symptoms:
                self.extracted_info['symptoms'] = symptoms
                self.extracted_info['doctor_assigned'] = True
                self.conversation_stage = 'datetime'
        
        # Extract date/time
        if self.extracted_info['doctor_assigned'] and not self.extracted_info['appointment_datetime']:
            dt = self._parse_datetime(message)
            if dt:
                self.extracted_info['appointment_datetime'] = dt
                self.conversation_stage = 'confirmation'
    
    def _check_availability_and_suggest(self, preferred_dt: datetime) -> Tuple[bool, Optional[datetime], List[datetime]]:
        """
        Check availability and suggest alternatives.
        
        Returns:
            (is_available, suggested_datetime, available_slots)
        """
        # Check for conflict
        has_conflict = self.calendar_service.check_conflict(preferred_dt)
        
        if not has_conflict:
            # Check if within business hours (9 AM - 5 PM)
            hour = preferred_dt.hour
            if 9 <= hour < 17:
                return (True, preferred_dt, [preferred_dt])
        
        # Get available slots for the day
        available_slots = self.calendar_service.get_available_slots(preferred_dt)
        
        # Suggest next available
        suggested = self.calendar_service.suggest_next_available(preferred_dt)
        
        return (False, suggested, available_slots[:5])  # Return top 5 slots
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and return agent response.
        
        Args:
            user_message: User's input message
        
        Returns:
            Agent's response
        """
        # Update extracted information
        self._update_extracted_info(user_message)
        
        # Add context about extracted information
        context = ""
        if self.extracted_info['patient_name']:
            context += f"\nPatient name: {self.extracted_info['patient_name']}\n"
        if self.extracted_info['symptoms']:
            context += f"Symptoms/Reason: {self.extracted_info['symptoms']}\n"
            context += f"Doctor assigned: {self.doctor_name}\n"
        if self.extracted_info['appointment_datetime']:
            dt = self.extracted_info['appointment_datetime']
            context += f"Requested appointment time: {dt.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        
        # Check availability if we have a datetime
        availability_info = ""
        if self.extracted_info['appointment_datetime'] and not self.extracted_info['confirmed']:
            preferred_dt = self.extracted_info['appointment_datetime']
            is_available, suggested, slots = self._check_availability_and_suggest(preferred_dt)
            
            if is_available:
                availability_info = f"\nThe requested time ({preferred_dt.strftime('%A, %B %d, %Y at %I:%M %p')}) is available!\n"
            else:
                availability_info = f"\nThe requested time is not available. "
                if suggested:
                    availability_info += f"Next available slot: {suggested.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
                if slots:
                    availability_info += f"Available slots today: {', '.join([s.strftime('%I:%M %p') for s in slots[:3]])}\n"
        
        # Build messages for LLM
        messages = self.memory.chat_memory.messages.copy()
        messages.append(HumanMessage(content=user_message))
        
        # Add context to the last message
        if context or availability_info:
            enhanced_message = user_message + "\n\n[Context]" + context + availability_info
            messages[-1] = HumanMessage(content=enhanced_message)
        
        # Check if user confirmed the appointment FIRST (before LLM response)
        # This ensures booking happens before the AI generates a response
        if not self.extracted_info['confirmed']:
            confirmation_keywords = ['yes', 'confirm', 'book it', 'schedule', 'that works', 'ok', 'sure', 'proceed', 'go ahead']
            if any(word in user_message.lower() for word in confirmation_keywords):
                if self.extracted_info['appointment_datetime'] and self.extracted_info['patient_name']:
                    # Book the appointment FIRST
                    try:
                        suggested_dt = self.extracted_info['appointment_datetime']
                        is_available, alternative_dt, _ = self._check_availability_and_suggest(suggested_dt)
                        
                        if is_available:
                            final_dt = suggested_dt
                        elif alternative_dt:
                            final_dt = alternative_dt
                        else:
                            return "I'm sorry, but I couldn't find an available time slot. Please try a different date or time."
                        
                        print(f"Attempting to create appointment for {self.extracted_info['patient_name']} at {final_dt}")
                        event = self.calendar_service.create_appointment(
                            patient_name=self.extracted_info['patient_name'],
                            appointment_time=final_dt,
                            doctor_name=self.doctor_name,
                            doctor_email=self.doctor_email
                        )
                        
                        # Verify event was created
                        if not event or not event.get('id'):
                            raise Exception("Event was not created - no event ID returned")
                        
                        self.extracted_info['confirmed'] = True
                        
                        # Get event details for confirmation
                        event_id = event.get('id', 'N/A')
                        event_link = event.get('htmlLink', '')
                        calendar_id = self.calendar_service.calendar_id
                        
                        # Return confirmation message immediately (don't call LLM)
                        response_text = (
                            f"✅ Appointment confirmed!\n\n"
                            f"Patient: {self.extracted_info['patient_name']}\n"
                            f"Date & Time: {final_dt.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
                            f"Doctor: {self.doctor_name}\n"
                            f"Calendar: {calendar_id}\n"
                            f"Event ID: {event_id}\n\n"
                        )
                        
                        if event_link:
                            response_text += f"📅 View in Calendar: {event_link}\n\n"
                        
                        response_text += (
                            f"Your appointment has been successfully added to your Google Calendar. "
                            f"Please check your calendar to verify it appears.\n\n"
                            f"Is there anything else I can help you with?"
                        )
                        
                        # Update memory and return immediately
                        self.memory.chat_memory.add_message(HumanMessage(content=user_message))
                        self.memory.chat_memory.add_message(AIMessage(content=response_text))
                        return response_text
                    except Exception as e:
                        import traceback
                        error_trace = traceback.format_exc()
                        print(f"ERROR creating appointment: {e}")
                        print(f"Traceback: {error_trace}")
                        response_text = f"I apologize, but there was an error booking your appointment: {str(e)}\n\nPlease try again or contact support."
                        # Update memory and return error
                        self.memory.chat_memory.add_message(HumanMessage(content=user_message))
                        self.memory.chat_memory.add_message(AIMessage(content=response_text))
                        return response_text
        
        # Get response from LLM (using invoke instead of deprecated __call__)
        # Only call LLM if we haven't already handled booking
        response = self.llm.invoke(messages)
        response_text = response.content
        
        # Update memory
        self.memory.chat_memory.add_message(HumanMessage(content=user_message))
        self.memory.chat_memory.add_message(AIMessage(content=response_text))
        
        return response_text
    
    def reset(self):
        """Reset the conversation and extracted information."""
        self.memory.clear()
        self.extracted_info = {
            'patient_name': None,
            'symptoms': None,
            'preferred_date': None,
            'preferred_time': None,
            'appointment_datetime': None,
            'doctor_assigned': False,
            'confirmed': False
        }
        self.conversation_stage = 'greeting'
        self._initialize_conversation()

