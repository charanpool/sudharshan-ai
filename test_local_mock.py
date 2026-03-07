"""
Sudharshan-AI: Enhanced Local Mock Test
Verifies AI + Behavioral Engine + Duress PIN logic with the new DB layer.
"""

import json
import sys
from unittest.mock import MagicMock, patch

# Add paths for local imports
sys.path.append("src/lambda/risk_analyzer")
sys.path.append("src/shared")
sys.path.append(".")

import handler

def run_enhanced_mock_test():
    print("🚀 Starting Sudharshan-AI Enhanced Mock Test...\n")

    # 1. Mock the DynamoClient (new db layer)
    mock_db = MagicMock()
    handler.db = mock_db
    handler.bedrock_analyzer = MagicMock()

    # 2. Configure mock return values
    mock_db.get_user_baseline.return_value = {
        "user_id": "user-456",
        "last_typing_speed": 45.0,
        "last_hesitation_count": 0,
        "last_screen_time": 3000,
    }
    mock_db.get_risk_profile.return_value = {
        "user_id": "user-456",
        "duress_pin_hash": "9999",
    }
    mock_db.update_baseline.return_value = True

    # --- SCENARIO 1: Duress PIN ---
    print("--- Testing Scenario 1: Duress PIN Trigger ---")
    duress_event = {
        "body": json.dumps({
            "session_id": "sess-duress",
            "user_id": "user-456",
            "signals": {"typing_speed_wpm": 45},
            "transaction": {
                "amount": 100,
                "recipient_type": "trusted",
                "entered_pin": "9999"
            }
        })
    }

    handler.bedrock_analyzer.analyze_transaction.return_value = (10, "Looks safe", None)

    response = handler.handler(duress_event, None)
    body = json.loads(response["body"])
    print(f"Risk Score: {body['risk_score']} | Decision: {body['decision']}")
    if body['risk_score'] == 100 and "Duress" in body['reasoning']:
        print("✅ Duress PIN logic verified.")
    else:
        print("❌ Duress PIN logic failed.")

    # --- SCENARIO 2: Behavioral Anomaly ---
    print("\n--- Testing Scenario 2: Behavioral Anomaly ---")
    handler.bedrock_analyzer.analyze_transaction.return_value = (5, "AI sees no scam pattern", None)

    # Return baseline for anomaly detection, no duress pin
    mock_db.get_risk_profile.return_value = {}

    anomaly_event = {
        "body": json.dumps({
            "session_id": "sess-anomaly",
            "user_id": "user-456",
            "signals": {
                "typing_speed_wpm": 15,
                "hesitation_count": 5,
                "tremor_intensity": 9,
                "is_on_call": True
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
    print("\n--- INVESTIGATION REPORT EXTRACT ---")
    print(body.get('investigation_report', 'Report not found'))

    if body['risk_score'] > 30:
        print("✅ Behavioral Engine logic verified: Score increased due to anomalies.")
    else:
        print("❌ Behavioral Engine failed to detect significant deviation.")

    # --- SCENARIO 3: DB Layer Integration ---
    print("\n--- Testing Scenario 3: DB Layer Integration ---")
    assert mock_db.get_user_baseline.called, "get_user_baseline was never called"
    assert mock_db.get_risk_profile.called, "get_risk_profile was never called"
    assert mock_db.update_baseline.called, "update_baseline was never called"
    print("✅ DynamoClient integration verified: All DB methods were called.")

if __name__ == "__main__":
    run_enhanced_mock_test()
