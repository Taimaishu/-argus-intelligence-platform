#!/bin/bash

# Tesseract OCR Installation Script for Argus Intelligence Platform
# This script installs Tesseract OCR and language data

echo "Installing Tesseract OCR..."

# Install Tesseract and language packs
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev

# Verify installation
if command -v tesseract &> /dev/null; then
    echo "Tesseract installed successfully!"
    tesseract --version
else
    echo "Tesseract installation failed. Please install manually."
    exit 1
fi

echo "Installation complete!"
