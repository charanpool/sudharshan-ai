import streamlit as st
import json
import uuid
import sys
import os
import importlib

# Ensure AWS region is set before loading boto3
if "AWS_DEFAULT_REGION" not in os.environ:
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# Add directories to sys.path so we can import without syntax errors
# 1. Add root for 'src.db...'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 2. Add risk_analyzer directory for 'handler' and 'utils...'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "lambda", "risk_analyzer"))

# Now we can just import the handler module directly
import handler
lambda_handler = handler.handler

from PIL import Image

favicon = Image.open("docs/assets/logo-transparent.png")
st.set_page_config(
    page_title="Sudharshan-AI Fraud Simulator",
    page_icon=favicon,
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

import base64

with open("docs/assets/logo-transparent.png", "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()

st.markdown(f"""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 0;">
    <img src="data:image/png;base64,{logo_b64}" width="50" style="vertical-align: middle;" />
    <h1 style="margin: 0; padding: 0;">Sudharshan-AI: Behavioral Fraud Detection</h1>
</div>
""", unsafe_allow_html=True)
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
        payload = {
            "session_id": f"streamlit-demo-{uuid.uuid4().hex[:8]}",
            "user_id": "demo-user-001",
            "transaction": {
                "amount": float(amount),
                "recipient_id": "recv-999" if recipient_type == "New/Unknown" else "recv-111",
                "recipient_type": recipient_type,
            },
            "signals": {
                "typing_speed_wpm": typing_speed,
                "hesitation_count": hesitation_count,
                "time_on_confirm_screen_ms": confirm_time_ms,
                "is_on_call": is_on_call,
                "time_of_day_hour": time_of_day,
                "tremor_intensity": tremor_intensity
            }
        }
        
        # Wrap in API Gateway event format
        event = {
            "body": json.dumps(payload)
        }
        
        try:
            # Invoke the lambda handler directly
            api_response = lambda_handler(event, None)
            response = json.loads(api_response["body"])
            
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
