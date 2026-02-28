#!/bin/bash
# Ollama Installation Script for Argus Intelligence Platform

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "Starting Ollama service..."
sudo systemctl start ollama
sudo systemctl enable ollama

echo ""
echo "Waiting for Ollama to start..."
sleep 5

echo ""
echo "Pulling embedding model (nomic-embed-text)..."
ollama pull nomic-embed-text

echo ""
echo "Pulling LLM model (llama3:8b)..."
ollama pull llama3:8b

echo ""
echo "Verifying installation..."
ollama list

echo ""
echo "✓ Ollama installation complete!"
echo ""
echo "Ollama is now running and ready to use with Argus Intelligence Platform"
echo "Models installed:"
echo "  - nomic-embed-text (for embeddings)"
echo "  - llama3:8b (for chat/LLM)"
