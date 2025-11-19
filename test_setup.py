"""
Test script to verify setup and configuration.
Run this before using the main application to ensure everything is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def check_environment():
    """Check if environment variables are set."""
    print("Checking environment variables...")
    
    required_vars = ['GEMINI_API_KEY']
    optional_vars = ['CALENDAR_ID', 'TIMEZONE', 'DOCTOR_NAME', 'DOCTOR_EMAIL']
    
    all_good = True
    
    for var in required_vars:
        if os.getenv(var):
            print(f"  ✓ {var} is set")
        else:
            print(f"  ✗ {var} is NOT set (REQUIRED)")
            all_good = False
    
    for var in optional_vars:
        if os.getenv(var):
            print(f"  ✓ {var} is set: {os.getenv(var)}")
        else:
            print(f"  ⚠ {var} is not set (using default)")
    
    return all_good


def check_credentials():
    """Check if Google credentials file exists."""
    print("\nChecking Google Calendar credentials...")
    
    if os.path.exists('credentials.json'):
        print("  ✓ credentials.json found")
        return True
    else:
        print("  ✗ credentials.json NOT found")
        print("    Please download it from Google Cloud Console")
        return False


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        'langchain',
        'langchain_google_genai',
        'google.auth',
        'googleapiclient',
        'dotenv',
        'pytz',
        'google.generativeai'
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            if package == 'google.auth':
                __import__('google.auth')
            elif package == 'googleapiclient':
                __import__('googleapiclient')
            else:
                __import__(package.replace('-', '_'))
            print(f"  ✓ {package} is installed")
        except ImportError:
            print(f"  ✗ {package} is NOT installed")
            all_installed = False
    
    return all_installed


def main():
    """Run all checks."""
    print("="*60)
    print("  Doctor Appointment Booking Agent - Setup Check")
    print("="*60)
    print()
    
    env_ok = check_environment()
    creds_ok = check_credentials()
    deps_ok = check_dependencies()
    
    print("\n" + "="*60)
    if env_ok and creds_ok and deps_ok:
        print("  ✓ All checks passed! You're ready to run the application.")
        print("\n  Run: python main.py")
        return 0
    else:
        print("  ✗ Some checks failed. Please fix the issues above.")
        print("\n  Common fixes:")
        if not env_ok:
            print("    - Create a .env file with OPENAI_API_KEY")
        if not creds_ok:
            print("    - Download credentials.json from Google Cloud Console")
        if not deps_ok:
            print("    - Run: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())


