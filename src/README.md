# Sudharshan-AI Source Code

This directory contains the core Lambda functions and shared utilities for the fraud detection system.

## Structure

```
src/
├── lambda/
│   └── risk_analyzer/      # Main risk analysis Lambda
│       ├── handler.py      # Lambda entry point
│       ├── bedrock_client.py  # Bedrock integration
│       ├── models.py       # Data models
│       └── requirements.txt
├── shared/
│   └── constants.py        # Shared constants
└── README.md
```

## Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r src/lambda/risk_analyzer/requirements.txt
```

## AWS Deployment

Deploy using AWS SAM or manually zip and upload to Lambda console.
