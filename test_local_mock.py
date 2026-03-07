"""
Sudharshan-AI: Enhanced Local Mock Test
Verifies AI + Behavioral Engine + Duress PIN logic.
"""

import json
import sys
from unittest.mock import MagicMock, patch

# Add paths for local imports
sys.path.append("src/lambda/risk_analyzer")
sys.path.append("src/shared")

import handler

def run_enhanced_mock_test():
    print("🚀 Starting Sudharshan-AI Enhanced Mock Test...")

    # 1. Setup Mocks for DynamoDB and Bedrock
    handler.bedrock_analyzer = MagicMock()
    handler.dynamodb = MagicMock()
    
    # 2. Mock Baseline Data (Normal user who is now jittery)
    mock_table = MagicMock()
    handler.dynamodb.Table.return_value = mock_table
    
    def mock_get_item(Key):
        if "user_id" in Key and Key["user_id"] == "user-456":
            # Normal baseline: fast typing, no hesitations, low tremor
            return {"Item": {
                "user_id": "user-456",
                "last_typing_speed": 45.0,
                "last_hesitation_count": 0,
                "last_screen_time": 3000,
                "duress_pin_hash": "9999"
            }}
        return {}
    
    mock_table.get_item.side_effect = mock_get_item

    # --- SCENARIO 1: Duress PIN ---
    print("\n--- Testing Scenario 1: Duress PIN Trigger ---")
    duress_event = {
        "body": json.dumps({
            "session_id": "sess-duress",
            "user_id": "user-456",
            "signals": {"typing_speed_wpm": 45},
            "transaction": {
                "amount": 100,
                "recipient_type": "trusted",
                "entered_pin": "9999"  # Matches mock_get_item "duress_pin_hash"
            }
        })
    }
    
    # Mock Bedrock for this (though Duress PIN should override)
    handler.bedrock_analyzer.analyze_transaction.return_value = (10, "Looks safe", None)
    
    response = handler.handler(duress_event, None)
    body = json.loads(response["body"])
    print(f"Risk Score: {body['risk_score']} | Decision: {body['decision']}")
    if body['risk_score'] == 100 and "Duress" in body['reasoning']:
        print("✅ Duress PIN logic verified.")
    else:
        print("❌ Duress PIN logic failed.")

    # --- SCENARIO 2: Behavioral Anomaly (AI safe, but user is jittery) ---
    print("\n--- Testing Scenario 2: Behavioral Anomaly ---")
    # AI returns low risk, but we simulate high tremors and hesitation which the behavioral engine should catch
    handler.bedrock_analyzer.analyze_transaction.return_value = (5, "AI sees no scam pattern", None)
    
    anomaly_event = {
        "body": json.dumps({
            "session_id": "sess-anomaly",
            "user_id": "user-456",
            "signals": {
                "typing_speed_wpm": 15,  # Much slower than baseline 45
                "hesitation_count": 5,   # High
                "tremor_intensity": 9,   # High
                "is_on_call": True       # Red flag
            },
            "transaction": {
                "amount": 5000,
                "recipient_type": "new"
            }
        })
    }
    
    response = handler.handler(anomaly_event, None)
    body = json.loads(response["body"])
    print(f"AI Risk: 5 | Final Risk: {body['risk_score']} | Decision: {body['decision']}")
    print(f"Reasoning: {body['reasoning']}")
    
    if body['risk_score'] > 30: # Behavioral engine should have pushed it up from 5
        print("✅ Behavioral Engine logic verified: Score increased due to anomalies.")
    else:
        print("❌ Behavioral Engine failed to detect significant deviation.")

if __name__ == "__main__":
    run_enhanced_mock_test()
