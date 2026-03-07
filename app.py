import streamlit as st
import json
import uuid
import sys
import os

import importlib.util

# Add root to pythonpath
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dynamically import handler because 'lambda' is a reserved keyword in Python
handler_path = os.path.join(os.path.dirname(__file__), "src", "lambda", "risk_analyzer", "handler.py")
spec = importlib.util.spec_from_file_location("handler", handler_path)
handler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler_module)
lambda_handler = handler_module.lambda_handler

st.set_page_config(
    page_title="Sudharshan-AI Fraud Simulator",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for UI
st.markdown("""
<style>
    .critical { color: #ff4b4b; font-weight: bold; }
    .caution { color: #faca2b; font-weight: bold; }
    .safe { color: #00cc96; font-weight: bold; }
    .report-box { background-color: #1e1e1e; padding: 15px; border-radius: 5px; font-family: monospace; color: #fff; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Sudharshan-AI: Behavioral Fraud Detection")
st.markdown("Simulate a UPI transaction and test the AI's ability to detect **psychological coercion** (like Digital Arrest) based purely on behavioral telemetry.")

with st.sidebar:
    st.header("⚙️ Transaction Setup")
    
    st.subheader("Financial Details")
    amount = st.number_input("Amount (INR)", min_value=1.0, value=100000.0, step=1000.0)
    recipient_type = st.selectbox("Recipient Type", ["Trusted/Saved", "New/Unknown", "Known Scammer"])
    time_of_day = st.slider("Time of Day (24h)", 0, 23, 14)
    
    st.subheader("Behavioral Telemetry")
    typing_speed = st.slider("Typing Speed (WPM)", 10, 100, 25, help="Low speed limits indicate hesitation.")
    hesitation_count = st.slider("Hesitations (>2s pauses)", 0, 15, 6, help="High pauses indicate external pressure.")
    confirm_time_ms = st.slider("Time on Confirm Screen (ms)", 1000, 30000, 15000, step=1000)
    tremor_intensity = st.slider("Gyroscope Tremor (0-10)", 0, 10, 8, help="High tremor implies physical shaking/stress.")
    is_on_call = st.checkbox("Active Phone Call During Tx", value=True, help="Scammers keep victims on the phone.")

st.subheader("🔍 Run Analysis")
if st.button("Analyze Transaction Risk", type="primary", use_container_width=True):
    with st.spinner("Analyzing behavioral signals with Amazon Nova..."):
        
        # Build the event payload matching AWS API Gateway
        event = {
            "session_id": f"streamlit-demo-{uuid.uuid4().hex[:8]}",
            "user_id": "demo-user-001",
            "amount": float(amount),
            "recipient_id": "recv-999" if recipient_type == "New/Unknown" else "recv-111",
            "recipient_type": recipient_type,
            "time_of_day": time_of_day,
            "behavioral_signals": {
                "typing_speed_wpm": typing_speed,
                "hesitation_count": hesitation_count,
                "time_on_confirm_screen_ms": confirm_time_ms,
                "is_on_call": is_on_call,
                "tremor_intensity": tremor_intensity
            }
        }
        
        try:
            # Invoke the lambda handler directly
            response = lambda_handler(event, None)
            
            # Display results
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            risk_score = response.get("risk_score", 0)
            decision = response.get("decision", "unknown").upper()
            
            if risk_score >= 70:
                color_class = "critical"
                icon = "🚨"
            elif risk_score >= 30:
                color_class = "caution"
                icon = "⚠️"
            else:
                color_class = "safe"
                icon = "✅"
                
            col1.metric("Risk Score", f"{risk_score}/100")
            col2.markdown(f"### Decision: <span class='{color_class}'>{icon} {decision}</span>", unsafe_allow_html=True)
            col3.metric("Matched Pattern", response.get("matched_pattern") or "None")
            
            st.markdown("### 🧠 AI Reasoning")
            st.info(response.get("reasoning", "No reasoning provided."))
            
            st.markdown("### 📄 Investigator Report")
            report = response.get("investigation_report", "No report generated.")
            st.markdown(f"<div class='report-box'>{report.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.info("Check if AWS credentials are valid and Tables are provisioned.")
