#!/bin/bash

echo "=========================================="
echo "Testing Service Connections"
echo "=========================================="
echo ""

# Test ML Service
echo "1. Testing ML Service (Port 5001)..."
ML_RESPONSE=$(curl -s http://localhost:5001/health 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✓ ML Service is running"
    echo "   Response: $ML_RESPONSE"
else
    echo "   ✗ ML Service is NOT running"
    echo "   Error: $ML_RESPONSE"
fi
echo ""

# Test Backend
echo "2. Testing Backend (Port 3001)..."
BACKEND_RESPONSE=$(curl -s http://localhost:3001/api/doctors 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✓ Backend is running"
    echo "   Response: ${BACKEND_RESPONSE:0:100}..."
else
    echo "   ✗ Backend is NOT running"
    echo "   Error: $BACKEND_RESPONSE"
fi
echo ""

# Test Chat Endpoint
echo "3. Testing Chat Endpoint..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","history":[]}' 2>&1)
if [ $? -eq 0 ]; then
    echo "   ✓ Chat endpoint is working"
    echo "   Response: ${CHAT_RESPONSE:0:200}..."
else
    echo "   ✗ Chat endpoint failed"
    echo "   Error: $CHAT_RESPONSE"
fi
echo ""

echo "=========================================="
echo "Test Complete"
echo "=========================================="

