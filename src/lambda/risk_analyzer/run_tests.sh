#!/bin/bash
# Sudharshan-AI: Offline Test Runner

# Ensure we are in the right directory
cd "$(dirname "$0")"

# Set PYTHONPATH to include src and shared
export PYTHONPATH=$PYTHONPATH:$(pwd)/..:$(pwd)/../../../shared

echo "🚀 Running Sudharshan-AI Offline Tests..."
pytest tests/ -v
