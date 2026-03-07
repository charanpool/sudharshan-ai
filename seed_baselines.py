"""
Sudharshan-AI: Baseline Seeder
Utility to populate DynamoDB with "normal" behavioral data for testing.
"""

import boto3
import time

def seed_data():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    
    # 1. Seed User Baselines
    baseline_table = dynamodb.Table("UserBaselines")
    print("Seeding UserBaselines...")
    
    baselines = [
        {
            "user_id": "user-456",
            "last_typing_speed": 40.0,
            "last_hesitation_count": 1,
            "last_screen_time": 4500,
            "is_on_call": False,
            "last_tremor_intensity": 1,
            "timestamp": int(time.time())
        },
        {
            "user_id": "victim-001",
            "last_typing_speed": 45.0,
            "last_hesitation_count": 0,
            "last_screen_time": 3000,
            "is_on_call": False,
            "last_tremor_intensity": 0,
            "timestamp": int(time.time())
        }
    ]
    
    for item in baselines:
        baseline_table.put_item(Item=item)
        print(f"  - Seeded baseline for {item['user_id']}")

    # 2. Seed Risk Profiles (for Duress PIN)
    profile_table = dynamodb.Table("RiskProfiles")
    print("Seeding RiskProfiles...")
    
    profiles = [
        {
            "user_id": "user-456",
            "duress_pin_hash": "9999", # Plain for MVP demo
            "alert_contacts": ["+919876543210"],
            "risk_tolerance": "medium"
        },
        {
            "user_id": "victim-001",
            "duress_pin_hash": "1111",
            "alert_contacts": ["family_member@email.com"],
            "risk_tolerance": "low"
        }
    ]
    
    for item in profiles:
        profile_table.put_item(Item=item)
        print(f"  - Seeded profile for {item['user_id']}")

if __name__ == "__main__":
    try:
        seed_data()
        print("\n✅ Seeding complete!")
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        print("Note: Ensure DynamoDB tables 'UserBaselines' and 'RiskProfiles' exist in us-east-1.")
