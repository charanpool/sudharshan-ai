"""
Sudharshan-AI: Database Seeder
Populates DynamoDB with demo behavioral baselines and risk profiles.

Usage:
    uv run python -m src.db.seed
"""

import sys
import os
from decimal import Decimal

# Allow running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.db.dynamo_client import DynamoClient


# ── Demo Data ────────────────────────────────────────────────────

DEMO_BASELINES = [
    {
        "user_id": "user-456",
        "last_typing_speed": Decimal("40.0"),
        "last_hesitation_count": 1,
        "last_screen_time": 4500,
        "is_on_call": False,
        "last_tremor_intensity": 1,
    },
    {
        "user_id": "victim-001",
        "last_typing_speed": Decimal("45.0"),
        "last_hesitation_count": 0,
        "last_screen_time": 3000,
        "is_on_call": False,
        "last_tremor_intensity": 0,
    },
]

DEMO_PROFILES = [
    {
        "user_id": "user-456",
        "duress_pin_hash": "9999",
        "alert_contacts": ["+919876543210"],
        "risk_tolerance": "medium",
    },
    {
        "user_id": "victim-001",
        "duress_pin_hash": "1111",
        "alert_contacts": ["family_member@email.com"],
        "risk_tolerance": "low",
    },
]


def seed_all():
    """Seed all demo data into DynamoDB."""
    db = DynamoClient()

    print("  📊 Seeding UserBaselines...")
    for item in DEMO_BASELINES:
        db.put_baseline(item)
        print(f"    → {item['user_id']}")

    print("  🔐 Seeding RiskProfiles...")
    for item in DEMO_PROFILES:
        db.put_risk_profile(item)
        print(f"    → {item['user_id']}")

    print("\n🎉 Seeding complete!")


if __name__ == "__main__":
    print("🌱 Sudharshan-AI: Seeding Demo Data...\n")
    try:
        seed_all()
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        print("Tip: Run 'uv run python -m src.db.provision' first to create the tables.")
