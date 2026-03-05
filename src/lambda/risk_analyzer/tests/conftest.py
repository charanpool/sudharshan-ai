import pytest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add relevant paths
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../shared"))

# Set required env vars for tests
os.environ["USER_BASELINES_TABLE"] = "UserBaselines"
os.environ["STATE_MACHINE_ARN"] = "arn:aws:states:us-east-1:123456789012:stateMachine:CircuitBreaker"

@pytest.fixture
def mock_boto3():
    # We patch the clients directly in the handler module since they are initialized at import time
    import handler
    
    with patch.object(handler, "dynamodb") as mock_dynamo, \
         patch.object(handler, "stepfunctions") as mock_step_client:
        
        mock_table = MagicMock()
        mock_dynamo.Table.return_value = mock_table
        
        yield {
            "dynamo": mock_dynamo,
            "table": mock_table,
            "step_client": mock_step_client
        }

@pytest.fixture
def mock_bedrock():
    with patch("bedrock_client.boto3.client") as mock_client:
        mock_runtime = MagicMock()
        mock_client.return_value = mock_runtime
        yield mock_runtime
