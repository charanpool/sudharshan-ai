"""
Sudharshan-AI: Data Models
Pydantic models for request/response validation.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Decision(Enum):
    """Transaction decision types."""
    APPROVE = "approve"
    DELAY = "delay"
    HOLD = "hold"


@dataclass
class BehavioralSignals:
    """Behavioral signals captured from the UPI app."""
    typing_speed_wpm: float = 0.0
    typing_rhythm_variance: float = 0.0
    hesitation_count: int = 0
    time_on_confirm_screen_ms: int = 0
    is_on_call: bool = False
    time_of_day_hour: int = 12
    tremor_intensity: int = 0


@dataclass
class TransactionContext:
    """Transaction metadata."""
    amount: float
    recipient_type: str  # "new", "known", "trusted"
    recipient_id: str
    is_first_transaction_to_recipient: bool = True


@dataclass
class RiskAnalysisRequest:
    """Request payload for risk analysis."""
    session_id: str
    user_id: str
    signals: BehavioralSignals
    transaction: TransactionContext


@dataclass
class RiskAnalysisResponse:
    """Response from risk analysis."""
    session_id: str
    risk_score: int  # 0-100
    decision: str
    reasoning: str
    matched_pattern: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON response."""
        return {
            "session_id": self.session_id,
            "risk_score": self.risk_score,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "matched_pattern": self.matched_pattern,
        }
