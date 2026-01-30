"""
Sudharshan-AI: Amazon Bedrock Client
Handles interaction with Claude Haiku for fraud pattern analysis.
"""

import json
import boto3
from typing import Tuple, Optional

import sys
sys.path.append("../../shared")
from constants import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, RISK_CATEGORIES


class BedrockFraudAnalyzer:
    """Client for analyzing transactions using Amazon Bedrock."""

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize Bedrock client."""
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name
        )
        self.model_id = BEDROCK_MODEL_ID

    def analyze_transaction(
        self,
        amount: float,
        recipient_type: str,
        behavioral_signals: dict,
        time_of_day: int
    ) -> Tuple[int, str, Optional[str]]:
        """
        Analyze a transaction for fraud risk using Claude Haiku.
        
        Args:
            amount: Transaction amount in INR
            recipient_type: "new", "known", or "trusted"
            behavioral_signals: Dict with typing patterns, hesitations, etc.
            time_of_day: Hour of day (0-23)
            
        Returns:
            Tuple of (risk_score, reasoning, matched_pattern)
        """
        prompt = self._build_prompt(amount, recipient_type, behavioral_signals, time_of_day)
        
        try:
            response = self._invoke_model(prompt)
            return self._parse_response(response)
        except Exception as e:
            # Fail open - if Bedrock fails, return medium risk
            return (50, f"Analysis unavailable: {str(e)}", None)

    def _build_prompt(
        self,
        amount: float,
        recipient_type: str,
        behavioral_signals: dict,
        time_of_day: int
    ) -> str:
        """Build the analysis prompt for Claude."""
        categories_list = "\n".join([f"- {k}: {v}" for k, v in RISK_CATEGORIES.items()])
        
        return f"""You are a fraud detection AI analyzing a UPI transaction for signs of psychological coercion.

TRANSACTION CONTEXT:
- Amount: ₹{amount:,.0f}
- Recipient: {recipient_type} contact
- Time: {time_of_day}:00 hours

BEHAVIORAL SIGNALS:
- Typing speed: {behavioral_signals.get('typing_speed_wpm', 'N/A')} WPM
- Hesitation count: {behavioral_signals.get('hesitation_count', 0)}
- Time on confirm screen: {behavioral_signals.get('time_on_confirm_screen_ms', 0)}ms
- User on phone call: {behavioral_signals.get('is_on_call', False)}

KNOWN SCAM PATTERNS:
{categories_list}

Analyze this transaction and respond in JSON format:
{{
    "risk_score": <0-100>,
    "reasoning": "<brief explanation>",
    "matched_pattern": "<pattern_key or null>"
}}

Be conservative: prioritize catching fraud over false positives."""

    def _invoke_model(self, prompt: str) -> str:
        """Invoke Claude Haiku via Bedrock."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": BEDROCK_MAX_TOKENS,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]

    def _parse_response(self, response_text: str) -> Tuple[int, str, Optional[str]]:
        """Parse Claude's JSON response."""
        try:
            # Extract JSON from response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
            
            data = json.loads(json_str)
            
            risk_score = min(100, max(0, int(data.get("risk_score", 50))))
            reasoning = data.get("reasoning", "No reasoning provided")
            matched_pattern = data.get("matched_pattern")
            
            return (risk_score, reasoning, matched_pattern)
        except (json.JSONDecodeError, KeyError, ValueError):
            return (50, "Unable to parse analysis", None)
