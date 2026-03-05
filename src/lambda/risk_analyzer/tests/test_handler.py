import pytest
from unittest.mock import MagicMock, patch
import json
import os
import sys

# Ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import handler

def test_handler_approve_scenario(mock_boto3):
    """Test a safe transaction that should be approved."""
    event = {
        "body": json.dumps({
            "session_id": "test-safe",
            "user_id": "user-1",
            "signals": {
                "typing_speed_wpm": 60,
                "hesitation_count": 0,
                "time_on_confirm_screen_ms": 2000,
                "is_on_call": False
            },
            "transaction": {
                "amount": 500,
                "recipient_type": "trusted"
            }
        })
    }
    
    # Mock Bedrock to return low risk
    with patch("handler.bedrock_analyzer.analyze_transaction") as mock_analyze:
        mock_analyze.return_value = (10, "Transaction looks safe.", None)
        
        response = handler.handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["decision"] == "approve"
        assert body["risk_score"] == 10
        
        # Verify DynamoDB update
        mock_boto3["table"].put_item.assert_called_once()
        # Verify Step Functions was NOT called
        mock_boto3["step_client"].start_execution.assert_not_called()

def test_handler_hold_scenario(mock_boto3):
    """Test a high risk transaction that should trigger a hold."""
    event = {
        "body": json.dumps({
            "session_id": "test-scam",
            "user_id": "user-victim",
            "signals": {
                "typing_speed_wpm": 20,
                "hesitation_count": 10,
                "time_on_confirm_screen_ms": 25000,
                "is_on_call": True
            },
            "transaction": {
                "amount": 95000,
                "recipient_type": "new"
            }
        })
    }
    
    # Mock Bedrock to return high risk
    with patch("handler.bedrock_analyzer.analyze_transaction") as mock_analyze:
        mock_analyze.return_value = (85, "Matches digital arrest pattern.", "digital_arrest")
        
        response = handler.handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["decision"] == "hold"
        assert body["risk_score"] == 85
        
        # Verify Step Functions WAS triggered
        mock_boto3["step_client"].start_execution.assert_called_once()
        args, kwargs = mock_boto3["step_client"].start_execution.call_args
        execution_input = json.loads(kwargs["input"])
        assert execution_input["decision"] == "hold"
        assert execution_input["session_id"] == "test-scam"

def test_handler_unusual_hour_hesitation(mock_boto3):
    """Test that unusual hours combined with hesitation increase risk."""
    event = {
        "body": json.dumps({
            "session_id": "test-night",
            "user_id": "user-1",
            "signals": {
                "typing_speed_wpm": 30,
                "hesitation_count": 4,
                "time_on_confirm_screen_ms": 10000,
                "is_on_call": False,
                "time_of_day_hour": 3 # 3 AM
            },
            "transaction": {
                "amount": 5000,
                "recipient_type": "new"
            }
        })
    }
    
    with patch("handler.bedrock_analyzer.analyze_transaction") as mock_analyze:
        # Simulate Bedrock identifying the odd timing and hesitation
        mock_analyze.return_value = (45, "Unusual hour and hesitation count.", None)
        
        response = handler.handler(event, None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["decision"] == "delay"

def test_handler_validation_error():
    """Test handler with missing required fields."""
    event = {"body": json.dumps({"session_id": "missing-rest"})}
    
    response = handler.handler(event, None)
    assert response["statusCode"] == 400
    assert "Missing required fields" in response["body"]
