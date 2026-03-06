"""
Sudharshan-AI: Duress PIN Handler
Handles the silent activation of the Duress PIN feature.
"""

import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stepfunctions = boto3.client("stepfunctions")
state_machine_arn = os.environ.get("STATE_MACHINE_ARN")

def handler(event, context):
    """
    Lambda handler for the Duress PIN silent alert.
    Triggered when a user enters a pre-configured 'Duress PIN' instead of their actual UPI PIN.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        session_id = body.get("session_id", "unknown_session")
        user_id = body.get("user_id", "unknown_user")
        
        logger.warning(f"🚨 DURESS PIN ACTIVATED for User: {user_id}, Session: {session_id}")
        
        # Trigger the circuit breaker with a HOLD decision immediately
        _trigger_duress_workflow(session_id, user_id)
        
        # Crucial for Duress workflow: Always return 200 OK resembling a normal transaction
        # so the coercer/scammer looking at the screen doesn't suspect the alert went out.
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "status": "processing",
                "message": "Transaction initiated securely.",
                "duress_activated": True # Hidden from UI but sent back for simulator testing
            })
        }
        
    except Exception as e:
        logger.error(f"Duress handler error: {str(e)}")
        # Fail safe
        return {"statusCode": 500, "body": json.dumps({"error": "Internal Error"})}


def _trigger_duress_workflow(session_id: str, user_id: str):
    """Trigger AWS Step Functions circuit breaker in DURESS mode."""
    if not state_machine_arn:
        logger.warning("STATE_MACHINE_ARN not configured, skipping duress workflow")
        return

    try:
        stepfunctions.start_execution(
            stateMachineArn=state_machine_arn,
            name=f"duress-{session_id}",
            input=json.dumps({
                "session_id": session_id,
                "user_id": user_id,
                "risk_score": 100,
                "decision": "hold",
                "reasoning": "DURESS PIN ACTIVATED: User explicitly signaled they are under coercion.",
                "is_duress": True
            })
        )
    except Exception as e:
        logger.error(f"Failed to trigger Step Functions for Duress: {str(e)}")

# Local Testing
if __name__ == "__main__":
    test_event = {
        "body": '{"user_id": "test-123", "device_id": "dev-456", "timestamp": "2026-03-05T00:00:00Z", "duress_pin": "9999"}'
    }
    try:
        print(handler(test_event, None))
    except Exception as e:
        print(f"Handler executed (bypassed AWS credentials error for local testing): {e}")
