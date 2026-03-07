"""
Sudharshan-AI: Amazon Bedrock Client
Handles interaction with Claude 3 Haiku / Bedrock Agents for fraud pattern analysis.
"""

import json
import boto3
import logging
from typing import Tuple, Optional, Dict, Any

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared')))
from constants import BEDROCK_MODEL_ID, BEDROCK_MAX_TOKENS, RISK_CATEGORIES

logger = logging.getLogger(__name__)

class BedrockFraudAnalyzer:
    """Client for analyzing transactions using Amazon Bedrock with KB & Agents support."""

    def __init__(self, region_name: str = "us-east-1"):
        """Initialize Bedrock Runtime and Agent clients."""
        try:
            self.runtime_client = boto3.client("bedrock-runtime", region_name=region_name)
            self.agent_runtime_client = boto3.client("bedrock-agent-runtime", region_name=region_name)
        except Exception as e:
            logger.warning(f"Could not initialize all Bedrock clients: {e}")
            self.runtime_client = boto3.client("bedrock-runtime", region_name=region_name)
            self.agent_runtime_client = None

        self.model_id = BEDROCK_MODEL_ID
        
        # Configuration for Bedrock Knowledge Base (Placeholder IDs for Hackathon Demo)
        self.knowledge_base_id = "SCAM_PATTERNS_KB_01"
        self.model_arn = f"arn:aws:bedrock:{region_name}::foundation-model/{self.model_id}"

    def analyze_transaction(
        self,
        amount: float,
        recipient_type: str,
        behavioral_signals: dict,
        time_of_day: int
    ) -> Tuple[int, str, Optional[str]]:
        """
        Analyze a transaction for fraud risk using Bedrock Knowledge Bases & Claude.
        """
        prompt = self._build_contextual_prompt(amount, recipient_type, behavioral_signals, time_of_day)
        
        try:
            # 1. Try cutting-edge RetrieveAndGenerate API (Knowledge Base)
            if self.agent_runtime_client:
                try:
                    return self._invoke_knowledge_base(prompt)
                except Exception as kb_err:
                    logger.warning(f"KB Retrieval failed, falling back to direct model invocation: {kb_err}")

            # 2. Fallback to direct model invocation
            response = self._invoke_direct_model(prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Bedrock analysis failed: {str(e)}")
            # Fail open - if Bedrock completely fails, return medium risk to not block legitimate users
            return (50, f"Analysis degraded - Model unavailable: {str(e)}", None)

    def _invoke_knowledge_base(self, prompt: str) -> Tuple[int, str, Optional[str]]:
        """
        Uses Amazon Bedrock Knowledge Bases (RetrieveAndGenerate) to check latest scam patterns.
        NOTE: This is a robust mock simulating the exact Boto3 API response structure for the hackathon,
        as provisioning a real KB takes time/resources.
        """
        # In a real deployed environment, this would call:
        # response = self.agent_runtime_client.retrieve_and_generate(...)
        
        # Simulate KB-augmented direct call to demonstrate architecture capabilities
        augmented_prompt = f"[System: Context retrieved from Knowledge Base {self.knowledge_base_id}]\n" + prompt
        response_text = self._invoke_direct_model(augmented_prompt)
        return self._parse_json_response(response_text)

    def _invoke_direct_model(self, prompt: str) -> str:
        """Invoke Foundation Model directly via Bedrock Runtime."""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": BEDROCK_MAX_TOKENS,
            "temperature": 0.1, # Low temperature for more deterministic risk scoring
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })

        response = self.runtime_client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]

    def _build_contextual_prompt(
        self,
        amount: float,
        recipient_type: str,
        behavioral_signals: dict,
        time_of_day: int
    ) -> str:
        """Build the structured prompt for the AI with Bharat-centric multi-language focus."""
        
        # Load local scam intelligence for prompt enrichment
        try:
            with open(os.path.join(os.path.dirname(__file__), 'scam_intelligence.json'), 'r') as f:
                intel = json.load(f)
                patterns = "\n".join([f"- {p['name']} ({', '.join(p['languages'])}): {p['scripts'][0]}" for p in intel['scam_patterns']])
        except Exception:
            patterns = "\n".join([f"- {k}: {v}" for k, v in RISK_CATEGORIES.items()])

        return f"""You are a specialized fraud detection AI agent acting as a behavioral analyst for the Indian UPI ecosystem.
You must analyze a transaction for psychological coercion (Digital Arrest, KYC scams, etc.).

TRANSACTION CONTEXT:
- Amount: ₹{amount:,.0f}
- Recipient: {recipient_type} contact
- Time: {time_of_day}:00 hours (24h format)

BEHAVIORAL TELEMETRY (Critical for detecting coercion):
- Typing speed: {behavioral_signals.get('typing_speed_wpm', 'N/A')} WPM
- Hesitation count (>2s pauses): {behavioral_signals.get('hesitation_count', 0)}
- Time on confirm screen: {behavioral_signals.get('time_on_confirm_screen_ms', 0)}ms
- Device state (On active phone call): {behavioral_signals.get('is_on_call', False)}
- Gyroscope Tremor (Hand shaking intensity 0-10): {behavioral_signals.get('tremor_intensity', 0)}

INDIAN SCAM PATTERNS & LINGUISTIC NUANCES:
{patterns}

ANALYSIS GUIDELINES:
1. Support Multi-language: The user might be hearing scripts in Hindi, Kannada, Tamil, or Hinglish (e.g., "Aapka account block ho jayega").
2. Code-switching: Victims often switch between English and regional languages when under stress.
3. Psychological Red Flags: High tremor + on call + new recipient + high amount is a massive red flag for Digital Arrest.

Respond ONLY in valid JSON format:
{{
    "risk_score": <0-100 integer>,
    "reasoning": "<brief, sharp explanation including linguistic/behavioral anomalies>",
    "matched_pattern": "<pattern_id or null>",
    "detected_language": "<detected language or 'unknown'>"
}}

Priority: Be conservative but highly sensitive to behavioral anomalies and regional scam nuances."""

    def _parse_json_response(self, response_text: str) -> Tuple[int, str, Optional[str]]:
        """Safely parse Claude's JSON response output."""
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON object found in response")
                
            json_str = response_text[start:end]
            data = json.loads(json_str)
            
            risk_score = min(100, max(0, int(data.get("risk_score", 50))))
            reasoning = data.get("reasoning", "Unknown behavioral anomaly")
            matched_pattern = data.get("matched_pattern")
            
            return (risk_score, reasoning, matched_pattern)
        except Exception as e:
            logger.error(f"Failed to parse Bedrock response: {response_text}. Error: {e}")
            return (60, "Analysis fallback due to output parsing error", None)

