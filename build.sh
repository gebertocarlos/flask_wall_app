#!/bin/sh
set -o errexit

echo "Python version:"
python --version

echo "Pip version:"
pip --version

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p static
mkdir -p instance
mkdir -p templates

echo "Initializing data files..."
touch posts.json
echo "[]" > posts.json

echo "Setting file permissions..."
chmod -R 755 .
chmod 666 posts.json

echo "Current directory contents:"
ls -la

echo "Build completed successfully!" 