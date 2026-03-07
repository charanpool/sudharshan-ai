"""
Sudharshan-AI: Infrastructure Provisioner
Creates the required DynamoDB tables.

Usage:
    uv run python -m src.db.provision
"""

import boto3
import sys
import os

# Allow running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.db.config import AWS_REGION, TABLE_SCHEMAS


def provision_tables():
    """Create all required DynamoDB tables if they don't already exist."""
    client = boto3.client("dynamodb", region_name=AWS_REGION)
    existing = client.list_tables()["TableNames"]

    for schema in TABLE_SCHEMAS:
        name = schema["TableName"]
        if name in existing:
            print(f"  ✓ Table '{name}' already exists. Skipping.")
            continue

        print(f"  ⏳ Creating table '{name}'...")
        client.create_table(**schema)

        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=name)
        print(f"  ✅ Table '{name}' is ACTIVE.")

    print("\n🎉 Infrastructure provisioning complete!")


if __name__ == "__main__":
    print("🏗️  Sudharshan-AI: Provisioning DynamoDB Tables...\n")
    try:
        provision_tables()
    except Exception as e:
        print(f"\n❌ Provisioning failed: {e}")
        print("Tip: Ensure your AWS credentials are configured and have DynamoDB permissions.")
