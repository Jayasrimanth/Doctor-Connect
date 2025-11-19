#!/bin/bash

echo "=========================================="
echo "Verifying Appointment in Calendar"
echo "=========================================="
echo ""

echo "1. Checking recent calendar events..."
echo ""

RESPONSE=$(curl -s http://localhost:5001/list_events 2>&1)

if [ $? -eq 0 ]; then
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo "   ✗ Could not connect to ML service"
    echo "   Make sure ML service is running on port 5001"
    echo ""
    echo "   Error: $RESPONSE"
fi

echo ""
echo "=========================================="
echo ""
echo "2. Check your Python ML Service terminal for:"
echo "   - '✅ Event created successfully!'"
echo "   - Event ID"
echo "   - Event Link (click to open in Google Calendar)"
echo ""
echo "3. Check Google Calendar:"
echo "   - Go to: https://calendar.google.com"
echo "   - Look for date: November 19th, 2025"
echo "   - Check your 'primary' calendar"
echo "   - Refresh the page"
echo ""
echo "=========================================="

