import json
import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "lambda", "risk_analyzer"))
from handler import handler

event = {
    "body": json.dumps({
        "session_id": f"streamlit-demo-{uuid.uuid4().hex[:8]}",
        "user_id": "demo-user-001",
        "amount": 100000.0,
        "recipient_id": "recv-111",
        "recipient_type": "Trusted/Saved",
        "time_of_day": 14,
        "behavioral_signals": {
            "typing_speed_wpm": 25,
            "hesitation_count": 6,
            "time_on_confirm_screen_ms": 15000,
            "is_on_call": True,
            "tremor_intensity": 8
        }
    })
}

print(handler(event, None))
