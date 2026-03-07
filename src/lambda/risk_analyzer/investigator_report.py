"""
Sudharshan-AI: Fraud Investigator Report Generator
Generates professional evidence fact-sheets for bank fraud officers.
"""

import json
from datetime import datetime

class InvestigatorReport:
    """Generates a human-readable investigation report from risk analysis data."""

    @staticmethod
    def generate(session_id: str, risk_data: dict, behavioral_data: dict) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        risk_score = risk_data.get("risk_score", 0)
        
        # Determine Severity
        severity = "LOW"
        if risk_score >= 70: severity = "CRITICAL / HOLD"
        elif risk_score >= 30: severity = "MEDIUM / DELAY"

        report = f"""
==========================================================
        SUDHARSHAN-AI: FRAUD INVESTIGATION REPORT
==========================================================
Generated: {timestamp}
Session ID: {session_id}
Risk Severity: {severity} ({risk_score}/100)
----------------------------------------------------------

1. EXECUTIVE SUMMARY
--------------------
Analysis indicates a {severity.lower()} risk transaction. 
AI Reason: {risk_data.get('reasoning', 'N/A')}
Matched Pattern: {risk_data.get('matched_pattern', 'Unknown')}

2. BEHAVIORAL ANOMALIES (TELEMETRY)
-----------------------------------
- Typing Speed: {behavioral_data.get('typing_speed_wpm', 'N/A')} WPM
- Hesitation Count: {behavioral_data.get('hesitation_count', 0)} (deviant)
- Hand Tremors (0-10): {behavioral_data.get('tremor_intensity', 0)}
- Active Phone Call: {"YES" if behavioral_data.get('is_on_call') else "NO"}

3. AI CONTEXTUAL MATCH (BHARAT INTELLIGENCE)
--------------------------------------------
The transaction behavior correlates with regional scam patterns 
identified in the National Indian Scam Database (Mock KB).
Specifically matches indicators for: {risk_data.get('matched_pattern', 'N/A')}

4. RECOMMENDED ACTION
---------------------
[ ] PROCEED: Low risk, no interference.
[ ] MONITOR: Medium risk, cooling period applied.
[X] INTERVENE: High risk, Silent Circuit Breaker triggered.

----------------------------------------------------------
Disclaimer: This report is AI-generated for advisor use.
==========================================================
"""
        return report

# For Demo Purposes
if __name__ == "__main__":
    dummy_risk = {
        "risk_score": 88,
        "reasoning": "High tremor and slow typing rhythm detected during active phone call. Matches 'Digital Arrest' script profile.",
        "matched_pattern": "DIGITAL_ARREST_001"
    }
    dummy_signals = {
        "typing_speed_wpm": 18,
        "hesitation_count": 9,
        "tremor_intensity": 8,
        "is_on_call": True
    }
    print(InvestigatorReport.generate("SESS-DEMO-99", dummy_risk, dummy_signals))
