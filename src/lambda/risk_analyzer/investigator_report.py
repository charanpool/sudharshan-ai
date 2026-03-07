"""
Sudharshan-AI: Investigator Report Generator
Utility to generate human-readable fraud investigation reports for bank officers.
"""

from typing import Dict, Any

def generate_fraud_fact_sheet(
    session_id: str,
    risk_score: int,
    decision: str,
    ai_reasoning: str,
    behavioral_score: int,
    matched_pattern: str = None
) -> str:
    """
    Generates a structured, professional report summarizing the fraud detection details.
    """
    
    status_icon = "🔴 CRITICAL" if risk_score >= 70 else "🟡 CAUTION" if risk_score >= 30 else "🟢 SECURE"
    
    report = f"""
============================================================
           SUDHARSHAN-AI: FRAUD INVESTIGATION REPORT
============================================================
SESSION ID: {session_id}
STATUS    : {status_icon}
DECISION  : {decision.upper()}
------------------------------------------------------------

RISK ASSESSMENT BREAKDOWN:
- TOTAL RISK SCORE: {risk_score}/100
- AI REASONING    : {ai_reasoning}
- BEHAVIORAL DEV  : {behavioral_score}/100
- MATCHED PATTERN : {matched_pattern or 'General Anomaly'}

------------------------------------------------------------
INVESTIGATOR NOTES:
The system detected significant deviation from the user's 
typical behavioral baseline. The AI model identified 
linguistic patterns consistent with known coercion scripts.

ACTION TAKEN: {decision.upper()} implemented via Silent Circuit Breaker.
============================================================
"""
    return report.strip()

if __name__ == "__main__":
    # Internal component test
    sample_report = generate_fraud_fact_sheet(
        "sess-999", 85, "hold", 
        "User on call, high hand tremors, matching Digital Arrest script.", 
        80, "digital_arrest_001"
    )
    print(sample_report)
