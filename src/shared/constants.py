"""
Sudharshan-AI Shared Constants
"""

# Risk Score Thresholds
RISK_THRESHOLD_LOW = 30      # Below this: Approve immediately
RISK_THRESHOLD_HIGH = 70     # Above this: Hold transaction

# Cooling Period (seconds)
COOLING_PERIOD_SECONDS = 300  # 5 minutes

# Bedrock Configuration
BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
BEDROCK_MAX_TOKENS = 512

# API Response Decisions
DECISION_APPROVE = "approve"
DECISION_DELAY = "delay"
DECISION_HOLD = "hold"

# Risk Categories
RISK_CATEGORIES = {
    "digital_arrest": "Digital Arrest / Authority Impersonation",
    "lottery_scam": "Lottery / Prize Scam",
    "kyc_fraud": "KYC Update Fraud",
    "investment_scam": "Investment / Ponzi Scheme",
    "relationship_scam": "Relationship / Romance Scam",
}
