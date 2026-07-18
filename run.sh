#!/bin/bash

# AI Student Performance Prediction System
# Startup script

echo "========================================"
echo "AI Student Performance Prediction System"
echo "========================================"

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python Version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p database model dataset logs uploads

# Train model if it doesn't exist
if [ ! -f "model/student_performance_model.pkl" ]; then
    echo "Training model (this may take a few minutes)..."
    python train_model.py
else
    echo "Model already trained"
fi

# Run the application
echo "Starting application..."
echo "Access the application at: http://localhost:5000"
python app.py
