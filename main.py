"""
Main entry point for the Doctor Appointment Booking Agent.
Provides a command-line interface for interacting with the AI agent.
"""

import os
import sys
from dotenv import load_dotenv
from calendar_service import CalendarService
from appointment_agent import AppointmentAgent

load_dotenv()


def print_welcome():
    """Print welcome message."""
    print("\n" + "="*60)
    print("  🏥 Doctor Appointment Booking Agent")
    print("="*60)
    print("\nHello! I'm your AI assistant for booking doctor appointments.")
    print("I can help you schedule an appointment by collecting your information")
    print("and checking availability in real-time.\n")
    print("Type 'quit' or 'exit' to end the conversation.\n")


def main():
    """Main function to run the appointment booking agent."""
    # Check for required environment variables
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please create a .env file with your Google Gemini API key.")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Check for credentials file
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found.")
        print("Please download it from Google Cloud Console and place it in the project root.")
        sys.exit(1)
    
    # Initialize calendar service
    try:
        calendar_id = os.getenv('CALENDAR_ID', 'primary')
        timezone = os.getenv('TIMEZONE', 'America/New_York')
        calendar_service = CalendarService(
            calendar_id=calendar_id,
            timezone=timezone
        )
        print("✓ Connected to Google Calendar")
    except Exception as e:
        print(f"Error initializing calendar service: {e}")
        sys.exit(1)
    
    # Initialize appointment agent
    try:
        doctor_name = os.getenv('DOCTOR_NAME', 'Dr. Smith')
        doctor_email = os.getenv('DOCTOR_EMAIL')
        agent = AppointmentAgent(
            calendar_service=calendar_service,
            doctor_name=doctor_name,
            doctor_email=doctor_email
        )
        print("✓ AI Agent initialized\n")
    except Exception as e:
        print(f"Error initializing appointment agent: {e}")
        sys.exit(1)
    
    # Start conversation
    print_welcome()
    
    # Initial greeting
    greeting = agent.chat("Hello")
    print(f"Agent: {greeting}\n")
    
    # Conversation loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print("\nAgent: Thank you for using our appointment booking service. Have a great day! 👋\n")
                break
            
            if user_input.lower() in ['reset', 'start over']:
                agent.reset()
                print("\nAgent: Conversation reset. How can I help you today?\n")
                continue
            
            # Get response from agent
            response = agent.chat(user_input)
            print(f"\nAgent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nAgent: Thank you for using our appointment booking service. Have a great day! 👋\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    main()


