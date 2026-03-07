"""
Sudharshan-AI: Behavioral Analysis Engine
Calculates deviation scores between current activity and historical user baselines.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def compute_behavioral_score(current_signals: Dict[str, Any], baseline: Dict[str, Any]) -> int:
    """
    Computes a 0-100 risk score based on how much current signals deviate from baseline.
    
    Weights:
    - Typing Speed (WPM): 30%
    - Hesitation Count: 20%
    - Screen Time: 20%
    - On Call (Binary): 20%
    - Tremor Intensity: 10%
    """
    if not baseline:
        logger.info("No baseline found for user. Returning neutral score (0).")
        return 0

    deviations = []

    # 1. Typing Speed Deviation (Normal: < 1.5 sigma)
    # Using a simple percentage deviation if sigma isn't available in MVP
    avg_wpm = baseline.get("last_typing_speed", 30.0)
    current_wpm = current_signals.get("typing_speed_wpm", 30.0)
    wpm_dev = abs(current_wpm - avg_wpm) / max(1, avg_wpm)
    deviations.append(min(1.0, wpm_dev) * 30)

    # 2. Hesitation Count (Threshold based)
    avg_hesitations = baseline.get("last_hesitation_count", 2)
    current_hesitations = current_signals.get("hesitation_count", 0)
    if current_hesitations > avg_hesitations * 3:
        deviations.append(20)
    elif current_hesitations > avg_hesitations * 2:
        deviations.append(10)

    # 3. Time on Screen (Anomalously long)
    avg_time = baseline.get("last_screen_time", 5000) # 5s default
    current_time = current_signals.get("time_on_confirm_screen_ms", 0)
    if current_time > avg_time * 4:
        deviations.append(20)
    elif current_time > avg_time * 2:
        deviations.append(10)

    # 4. On active call (High correlation with Digital Arrest)
    # Historically rarely on call during payments?
    if current_signals.get("is_on_call", False):
        deviations.append(20)

    # 5. Hand Tremor (Physical distress indicator)
    tremor = current_signals.get("tremor_intensity", 0) # 0-10
    if tremor >= 8:
        deviations.append(10)
    elif tremor >= 5:
        deviations.append(5)

    final_score = int(sum(deviations))
    logger.info(f"Behavioral Score Calculated: {final_score}/100 based on {len(deviations)} deviations.")
    
    return min(100, final_score)
