"""
Sudharshan-AI: Database Configuration
Centralized table names, region, and schema definitions.
"""

import os

# AWS Region
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# DynamoDB Table Names
USER_BASELINES_TABLE = os.environ.get("USER_BASELINES_TABLE", "UserBaselines")
RISK_PROFILES_TABLE = os.environ.get("RISK_PROFILES_TABLE", "RiskProfiles")

# Table Schemas (used by provisioning)
TABLE_SCHEMAS = [
    {
        "TableName": USER_BASELINES_TABLE,
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "user_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": RISK_PROFILES_TABLE,
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "user_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
]
