"""
Sudharshan-AI: Risk Analyzer Lambda Handler
Main entry point for transaction risk analysis.
"""

import os
import json
import logging
import boto3
from typing import Any
from models import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
    BehavioralSignals,
    TransactionContext,
)
from bedrock_client import BedrockFraudAnalyzer

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared')))
from constants import (
    RISK_THRESHOLD_LOW,
    RISK_THRESHOLD_HIGH,
    DECISION_APPROVE,
    DECISION_DELAY,
    DECISION_HOLD,
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
stepfunctions = boto3.client("stepfunctions")
table_name = os.environ.get("USER_BASELINES_TABLE", "UserBaselines")
state_machine_arn = os.environ.get("STATE_MACHINE_ARN")

# Initialize Bedrock client
bedrock_analyzer = BedrockFraudAnalyzer()


def handler(event: dict, context: Any) -> dict:
    """
    Lambda handler for risk analysis.
    
    Args:
        event: API Gateway event with transaction data
        context: Lambda context
        
    Returns:
        API Gateway response with risk assessment
    """
    try:
        # Parse request
        body = json.loads(event.get("body", "{}"))
        request = _parse_request(body)
        
        logger.info(f"Analyzing session: {request.session_id}")
        
        # Analyze with Bedrock
        risk_score, reasoning, matched_pattern = bedrock_analyzer.analyze_transaction(
            amount=request.transaction.amount,
            recipient_type=request.transaction.recipient_type,
            behavioral_signals={
                "typing_speed_wpm": request.signals.typing_speed_wpm,
                "hesitation_count": request.signals.hesitation_count,
                "time_on_confirm_screen_ms": request.signals.time_on_confirm_screen_ms,
                "is_on_call": request.signals.is_on_call,
                "tremor_intensity": request.signals.tremor_intensity,
            },
            time_of_day=request.signals.time_of_day_hour,
        )
        
        # Determine decision based on risk score
        decision = _determine_decision(risk_score)
        
        # Trigger Step Functions for HOLD or DELAY
        if decision in [DECISION_HOLD, DECISION_DELAY]:
            _trigger_workflow(request.session_id, risk_score, decision, reasoning)
            
        # Update user baseline in DynamoDB (Async-like pattern)
        _update_user_baseline(request.user_id, request.signals)
        
        # Build response
        response = RiskAnalysisResponse(
            session_id=request.session_id,
            risk_score=risk_score,
            decision=decision,
            reasoning=reasoning,
            matched_pattern=matched_pattern,
        )
        
        logger.info(f"Risk score: {risk_score}, Decision: {decision}")
        
        return _build_response(200, response.to_dict())
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return _build_response(400, {"error": str(e)})
    except Exception as e:
        logger.error(f"Internal error: {str(e)}")
        return _build_response(500, {"error": "Internal server error"})


def _parse_request(body: dict) -> RiskAnalysisRequest:
    """Parse and validate the request body."""
    signals_data = body.get("signals", {})
    transaction_data = body.get("transaction", {})
    
    if not body.get("session_id") or not body.get("user_id"):
        raise ValueError("Missing required fields: session_id, user_id")
    
    if not transaction_data.get("amount"):
        raise ValueError("Missing required field: transaction.amount")
    
    # Adding tremor_intensity for innovation criteria points
    signals = BehavioralSignals(
        typing_speed_wpm=signals_data.get("typing_speed_wpm", 0),
        typing_rhythm_variance=signals_data.get("typing_rhythm_variance", 0),
        hesitation_count=signals_data.get("hesitation_count", 0),
        time_on_confirm_screen_ms=signals_data.get("time_on_confirm_screen_ms", 0),
        is_on_call=signals_data.get("is_on_call", False),
        time_of_day_hour=signals_data.get("time_of_day_hour", 12),
        tremor_intensity=signals_data.get("tremor_intensity", 0),
    )
    
    transaction = TransactionContext(
        amount=float(transaction_data["amount"]),
        recipient_type=transaction_data.get("recipient_type", "new"),
        recipient_id=transaction_data.get("recipient_id", "unknown"),
        is_first_transaction_to_recipient=transaction_data.get("is_first", True),
    )
    
    return RiskAnalysisRequest(
        session_id=body["session_id"],
        user_id=body["user_id"],
        signals=signals,
        transaction=transaction,
    )


def _determine_decision(risk_score: int) -> str:
    """Determine transaction decision based on risk score."""
    if risk_score < RISK_THRESHOLD_LOW:
        return DECISION_APPROVE
    elif risk_score < RISK_THRESHOLD_HIGH:
        return DECISION_DELAY
    else:
        return DECISION_HOLD


def _trigger_workflow(session_id: str, risk_score: int, decision: str, reasoning: str):
    """Trigger AWS Step Functions circuit breaker."""
    if not state_machine_arn:
        logger.warning("STATE_MACHINE_ARN not configured, skipping workflow")
        return

    try:
        stepfunctions.start_execution(
            stateMachineArn=state_machine_arn,
            name=f"alert-{session_id}",
            input=json.dumps({
                "session_id": session_id,
                "risk_score": risk_score,
                "decision": decision,
                "reasoning": reasoning
            })
        )
    except Exception as e:
        logger.error(f"Failed to trigger Step Functions: {str(e)}")


def _update_user_baseline(user_id: str, signals: BehavioralSignals):
    """Update user's behavioral baseline in DynamoDB."""
    try:
        table = dynamodb.Table(table_name)
        # Simplified: Just store current signals as 'last_known' for the MVP
        table.put_item(
            Item={
                "user_id": user_id,
                "last_typing_speed": signals.typing_speed_wpm,
                "last_hesitation_count": signals.hesitation_count,
                "last_screen_time": signals.time_on_confirm_screen_ms,
                "is_on_call": signals.is_on_call,
                "last_tremor_intensity": signals.tremor_intensity,
                "timestamp": int(json.loads(json.dumps(signals.time_of_day_hour))) # hack for simple numeric
            }
        )
    except Exception as e:
        logger.error(f"Failed to update DynamoDB: {str(e)}")


def _build_response(status_code: int, body: dict) -> dict:
    """Build API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


# For local testing
if __name__ == "__main__":
    test_event = {
        "body": json.dumps({
            "session_id": "test-123",
            "user_id": "user-456",
            "signals": {
                "typing_speed_wpm": 25,
                "hesitation_count": 8,
                "time_on_confirm_screen_ms": 15000,
                "is_on_call": True,
                "time_of_day_hour": 14,
                "tremor_intensity": 8
            },
            "transaction": {
                "amount": 100000,
                "recipient_type": "new",
                "recipient_id": "scammer@upi",
            }
        })
    }
    
    result = handler(test_event, None)
    print(json.dumps(json.loads(result["body"]), indent=2))
