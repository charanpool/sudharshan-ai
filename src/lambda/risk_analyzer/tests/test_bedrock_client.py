import pytest
from unittest.mock import MagicMock, patch
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from bedrock_client import BedrockFraudAnalyzer

def test_bedrock_analyze_transaction(mock_bedrock):
    """Test parsing of Bedrock's response."""
    analyzer = BedrockFraudAnalyzer()
    
    # Mock successful response from Claude
    mock_response = {
        "body": MagicMock()
    }
    mock_response["body"].read.return_value = json.dumps({
        "content": [
            {
                "text": '{"risk_score": 75, "reasoning": "High hesitation and large amount", "matched_pattern": "digital_arrest"}'
            }
        ]
    }).encode("utf-8")
    
    mock_bedrock.invoke_model.return_value = mock_response
    
    score, reason, pattern = analyzer.analyze_transaction(
        amount=50000,
        recipient_type="new",
        behavioral_signals={"typing_speed_wpm": 20, "hesitation_count": 5},
        time_of_day=2
    )
    
    assert score == 75
    assert "High hesitation" in reason
    assert pattern == "digital_arrest"

def test_bedrock_fail_open(mock_bedrock):
    """Test that it fails open with medium risk if Bedrock errors."""
    analyzer = BedrockFraudAnalyzer()
    mock_bedrock.invoke_model.side_effect = Exception("Service unavailable")
    
    score, reason, pattern = analyzer.analyze_transaction(
        amount=1000,
        recipient_type="trusted",
        behavioral_signals={},
        time_of_day=12
    )
    
    assert score == 50
    assert "Analysis unavailable" in reason
    assert pattern is None
