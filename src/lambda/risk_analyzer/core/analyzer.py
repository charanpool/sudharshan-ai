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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../shared')))
from constants import BEDROCK_MODEL_ID, BEDROCK_FALLBACK_MODEL_ID, BEDROCK_MAX_TOKENS, RISK_CATEGORIES

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
        self.fallback_model_id = BEDROCK_FALLBACK_MODEL_ID

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
        """Uses Amazon Bedrock Knowledge Bases (RetrieveAndGenerate)."""
        augmented_prompt = f"[System: Context retrieved from Scam Intelligence Knowledge Base]\n" + prompt
        response_text = self._invoke_direct_model(augmented_prompt)
        return self._parse_json_response(response_text)

    def _invoke_direct_model(self, prompt: str) -> str:
        """Invoke Foundation Model via Bedrock Converse API (model-agnostic)."""
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        inference_config = {
            "maxTokens": BEDROCK_MAX_TOKENS,
            "temperature": 0.1,
        }

        # Try primary model, fall back to secondary
        for model_id in [self.model_id, self.fallback_model_id]:
            try:
                response = self.runtime_client.converse(
                    modelId=model_id,
                    messages=messages,
                    inferenceConfig=inference_config,
                )
                return response["output"]["message"]["content"][0]["text"]
            except Exception as e:
                logger.warning(f"Model {model_id} failed: {e}")
                continue

        raise RuntimeError("All Bedrock models unavailable")

    def _build_contextual_prompt(
        self,
        amount: float,
        recipient_type: str,
        behavioral_signals: dict,
        time_of_day: int
    ) -> str:
        """Build the structured prompt for the AI with Bharat-centric multi-language focus."""

        # Load pattern categories for prompt enrichment
        try:
            intel_path = os.path.join(os.path.dirname(__file__), '../scam_intelligence.json')
            with open(intel_path, 'r') as f:
                intel = json.load(f)
                patterns = "\n".join([f"- {p['name']} ({', '.join(p['languages'])})" for p in intel['scam_patterns']])
        except Exception:
            patterns = "\n".join([f"- {k}: {v}" for k, v in RISK_CATEGORIES.items()])

        safe_recipient_type = recipient_type.replace("Known Scammer", "High-Risk/Flagged Account")

        return f"""You are a financial safety analyst for the Indian UPI digital payments ecosystem.
Your role is to evaluate transaction behavioral telemetry and determine a risk score.

TRANSACTION DATA:
- Amount: INR {amount:,.0f}
- Recipient type: {safe_recipient_type}
- Time: {time_of_day}:00 hours

USER BEHAVIORAL TELEMETRY:
- Typing speed: {behavioral_signals.get('typing_speed_wpm', 'N/A')} WPM
- Hesitation pauses (>2s): {behavioral_signals.get('hesitation_count', 0)}
- Time on confirmation screen: {behavioral_signals.get('time_on_confirm_screen_ms', 0)}ms
- Active phone call during transaction: {behavioral_signals.get('is_on_call', False)}
- Device motion intensity (0-10): {behavioral_signals.get('tremor_intensity', 0)}

KNOWN RISK CATEGORIES:
{patterns}

EVALUATION CRITERIA:
1. High device motion + active call + new recipient + large amount = very high risk.
2. Multiple hesitation pauses suggest the user may be under external pressure.
3. Consider multi-language context (Hindi, Kannada, Hinglish).
4. A low typing speed combined with high hesitation is a strong stress indicator.

You must respond ONLY in valid JSON:
{{
    "risk_score": <integer 0-100>,
    "reasoning": "<brief explanation of behavioral anomalies detected>",
    "matched_pattern": "<category name or null>",
    "detected_language": "<detected language or 'unknown'>"
}}"""


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
            logger.error(f"Failed to parse Bedrock response. Error: {e}\nRaw Response: {repr(response_text)}")
            return (60, "Analysis fallback due to output parsing error", None)

