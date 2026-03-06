# Building a Real-Time Fraud Sentinel with Amazon Bedrock and Behavioral Biometrics

*By Sai Charan Koppuravuri | AI for Bharat Hackathon 2026*

## The Rise of Psychological Fraud

In H1 2024 alone, India lost over ₹1,750 crore to cyber fraud. A terrifying trend dominating these statistics is Authorized Push Payment (APP) fraud—specifically, "Digital Arrest" scams. Attackers impersonate authorities, psychologically coerce victims via phone calls, and manipulate them into transferring their life savings.

Because the victim physically authorizes the payment, traditional rule-based fraud systems (which flag unusual locations or devices) fail completely. The banking system assumes the transaction is legitimate because the credentials are correct.

**We needed a system that protects the human mind, not just the bank account.** That’s why I built **Sudharshan-AI**.

## Enter Sudharshan-AI

Sudharshan-AI is a real-time behavioral biometric protection layer for the UPI ecosystem. It doesn't rely solely on financial history. Instead, it looks at *how* the user is interacting with their device during the transaction.

By analyzing typing speed variance, hesitation counts (pauses >2 seconds before hitting "Pay"), device state (active phone calls), and even Gyroscope micro-tremors (hand shaking), we can detect the physical manifestations of fear and coercion.

But correlating all these subtle signals in real-time requires powerful AI.

## The AWS Architecture

To make this work securely and at scale, I leveraged a serverless AWS architecture, strictly utilizing **Amazon Bedrock** for intelligent decision-making.

### 1. The Real-Time Telemetry Ingestion (API Gateway & Lambda)
When a user initiates a transaction on the mockup UPI app, an event containing the financial data *and* the behavioral telemetry is sent to API Gateway, triggering a Python 3.9 Lambda function (`RiskAnalyzerFunction`). 

### 2. The Brain: Bedrock Knowledge Bases & Agents
Detecting fraud isn't static. Scammers change their scripts weekly. To future-proof the AI, I implemented a pattern mimicking **Amazon Bedrock Knowledge Bases**. 

By storing known scam patterns (like the FedEx scam, Customs scam, and Digital Arrest scripts) in a Knowledge Base, the Bedrock Agent (powered by **Claude 3 Haiku** for sub-second latency) retrieves the latest context and analyzes the user's live telemetry against it.

```python
# The Agentic Prompting Strategy
prompt = f"""You are a specialized fraud detection AI agent.
Analyze this telemetry heavily. High tremor + on call + large amount is a massive red flag for Digital Arrest.

BEHAVIORAL TELEMETRY:
- Hesitation count (>2s pauses): {signals.hesitation_count}
- Device state: On active phone call
- Gyroscope Tremor (0-10): {signals.tremor_intensity}

KNOWN SCAM PATTERNS TO MATCH: {retrieved_kb_context}
"""
```

Claude Haiku is exceptionally fast, allowing us to enforce a strict latency budget, outputting a precise `risk_score` and a natural language `reasoning` string explaining *why* the user behavior looks coerced.

### 3. The Silent Circuit Breaker (AWS Step Functions)
If the Bedrock Agent returns a high risk score, the Lambda function triggers an **AWS Step Functions** state machine. 

This is crucial for the "Silent" aspect of the Sentinel. If we simply blocked the transaction on the phone, the scammer (who is on the line) would know and could force the victim to try another bank. Instead, the Step Function executes a `DELAY` or `HOLD` state. The UI shows "Processing," while the backend silently alerts the bank's fraud team.

To visualize this, I built a dark-mode **Bank Admin Risk Dashboard** displaying the real-time AI reasoning from Bedrock.

### 4. The Duress PIN
As a final layer of protection, I added a "Duress API." Users can set a secondary PIN. If they are held at knifepoint or forced to pay, entering the Duress PIN returns a 200 OK to the phone (fooling the attacker) while simultaneously triggering the Step Function to freeze the account.

## Conclusion

By combining the low-latency intelligence of Amazon Bedrock with Lambda and Step Functions, we built a system capable of interpreting human anxiety in real-time. 

Sudharshan-AI is completely PII-free; we don't need to know *who* you are, we just need to know if you are safe. In the age of AI-generated voices and advanced social engineering, protecting the user's psychology is the next frontier of cybersecurity.
