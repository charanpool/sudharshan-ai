# Sudharshan-AI: Video Pitch Script
**Target Duration:** 3 Minutes
**Audience:** Judges for AI for Bharat Hackathon (AWS & Hack2Skill)
**Key Focus:** Technical depth, meaningful AI use, impact on India.

---

### [0:00 - 0:30] The Hook (The Problem)
**Visuals:** Dark screen. A news headline flashes: *"India loses ₹1,750 crore to cyber fraud in H1 2024."* Followed by a frantic WhatsApp message mockup from "CBI Officer".

**Voiceover:** 
"Imagine receiving a call. The caller claims to be the police. They say your Aadhaar is linked to money laundering, and if you don't transfer your funds to a 'safe account' immediately... you will be digitally arrested. 
You panic. Your hands shake. You open your UPI app and send your life savings over.
Current banking systems won't stop this, because *you* authorized it. They protect the account, but they don't protect the *mind*. 
Until today."

### [0:30 - 1:15] The Solution (Sudharshan-AI)
**Visuals:** Cut to the clean, royal blue Sudharshan-AI logo. Then show a side-by-side of the Simulator UI and the Admin Risk Dashboard. 

**Voiceover:**
"Welcome to Sudharshan-AI. The first privacy-first, real-time behavioral fraud sentinel for the UPI and OCEN ecosystem.
Instead of looking at just the transaction amount, Sudharshan-AI looks at *how* the user is interacting with their device. 
Are they hesitating before typing their PIN? Is there a drastic change in their typing speed? Is the phone's gyroscope detecting severe hand tremors indicating fear? Are they actively on a phone call while transferring a large sum of money?"

### [1:15 - 2:00] The Tech Stack (AWS Deep Dive)
**Visuals:** Bring up the Architecture Diagram (`template.yaml` visualization). Highlight AWS Bedrock, Lambda, and Step Functions.

**Voiceover:**
"To process telecom and behavioral telemetry in under a second without heavy mobile compute, we built a serverless enterprise architecture on AWS.
When a transaction is initiated, an API Gateway triggers our Risk Analyzer Lambda. 
Here is where the magic happens: We utilize **Amazon Bedrock Knowledge Bases and Agents**, powered by Claude 3 Haiku. The Agent retrieves the latest psychological coercion patterns—like the FedEx or Digital Arrest scam—and analyzes the live telemetry matrix. 
If Bedrock detects severe anomalies, it outputs a high risk score, immediately triggering our **AWS Step Functions Circuit Breaker**."

### [2:00 - 2:40] The Demo ("Wow" Factor)
**Visuals:** Live demo of the `simulator/index.html`. 
1. Show normal transaction (Safe).
2. Show User turning on "Currently on call" and dragging "Gyro Tremor" to 8/10. 
3. The phone mockup visibly screen-shakes. The user hits 'Pay'.
4. The Risk Ring turns RED! "SHIELD ACTIVATED".
5. Cut to the `dashboard/index.html` showing the live 'Critical Intervention' stream.

**Voiceover:**
"Let's see it in action. A normal transaction goes through instantly. But look what happens when telemetry indicates the user is on a call, and the gyroscope detects shaking hands.
The moment they press 'Pay', the Bedrock Agent recognizes the Digital Arrest pattern. The Step Function circuit breaker silently holds the funds. 
On the Bank Admin Dashboard, the SOC analyst gets a real-time, AI-generated reasoning report, allowing them to intercept the victim before the money is lost forever."

### [2:40 - 3:00] The Future & Sign-off
**Visuals:** Show roadmap (Duress PIN, Edge AI). Team members' contact info.

**Voiceover:**
"We've also designed a 'Duress PIN'—a secret PIN victims can enter to deliberately trigger this silent alarm.
Sudharshan-AI is fully PII-free, compliant with the DPDP Act, and scalable. 
We don't just detect stolen cards. We use AWS AI to detect stolen minds. 
Thank you."
