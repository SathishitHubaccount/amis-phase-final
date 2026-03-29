#!/bin/bash

echo "================================================"
echo "AMIS - Autonomous Manufacturing Intelligence"
echo "Quick Setup Script"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo ""
    echo "Please create .env file with your API key:"
    echo "    ANTHROPIC_API_KEY=your-key-here"
    echo ""
    echo "See .env.example for template"
    exit 1
fi

echo "[1/4] Checking .env file... OK"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not found! Please install Python 3.9+"
    exit 1
fi
echo "[2/4] Python found... OK"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found! Please install Node.js 18+"
    exit 1
fi
echo "[3/4] Node.js found... OK"
echo ""

# Install dependencies
echo "[4/4] Installing dependencies..."
echo ""

echo "Installing backend dependencies..."
cd backend
pip3 install -r requirements.txt --quiet
cd ..
echo "Backend dependencies installed!"
echo ""

echo "Installing frontend dependencies (this may take a minute)..."
cd frontend
npm install --silent
cd ..
echo "Frontend dependencies installed!"
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To start AMIS:"
echo ""
echo "1. Open TWO terminal windows"
echo ""
echo "2. Terminal 1 - Backend:"
echo "   cd backend"
echo "   python3 main.py"
echo ""
echo "3. Terminal 2 - Frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open browser to: http://localhost:5173"
echo ""
echo "================================================"
