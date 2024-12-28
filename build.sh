#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p static
mkdir -p instance

echo "Initializing data files..."
if [ ! -f posts.json ]; then
    echo "Creating posts.json..."
    echo "[]" > posts.json
    chmod 666 posts.json
fi

echo "Setting file permissions..."
chmod -R 755 static
chmod -R 755 templates
chmod 755 app.py

echo "Build completed successfully!" 