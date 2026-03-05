# Sudharshan-AI: Product Vision & Documentation

**"Privacy-First Fraud Prevention for the OCEN & UPI Ecosystem"**

---

## 🏛️ Project Goal
Sudharshan-AI is a real-time, behavioral biometric protection layer that detects psychological coercion (e.g., Digital Arrest, KYC Scams) *during* the transaction process. It focuses on the behavioral signals of the victim rather than the criminal's bank account, making it resilient to "mule account" rotations.

---

## 🛠️ Current Implementation (V1 Prototype)

### 1. Behavioral Telemetry Layer
The simulator currently captures and analyzes:
*   **Typing Speed (WPM)**: Real-time calculation of digit entry speed.
*   **Hesitation Count**: Tracks pauses > 2000ms, identifying "coached" behavior.
*   **Keystroke Variance**: Measures the "staccato" vs "rhythmic" nature of interaction to detect stress.
*   **Call Status**: Integration with device state to know if a user is on a call during the transaction.

### 2. AI Risk Analyzer (Bedrock)
*   **Model**: Amazon Bedrock (Claude 3 Haiku) for sub-second analysis.
*   **Scam Patterns**: Curated knowledge base of India-specific scam tactics (Digital Arrest, Lottery, FedEx scams).
*   **Fail-Open Logic**: High-availability design that defaults to "Safe/Delay" if the AI service is unreachable, ensuring no legitimate user is blocked.

### 3. Circuit Breaker Workflow (Step Functions)
*   **Safety Interventions**: 
    - **APPROVE**: Low risk, immediate processing.
    - **DELAY**: 5-minute cooling-off period for medium risk.
    - **HOLD**: SHIELD activation for high-risk detected patterns.

---

## 🚀 Future Roadmap & Extensions

### 1. Advanced Interaction Layer
*   **Flight Time**: Measuring the exact time taken to move between keys.
*   **Dwell Time**: How long a finger stays on a specific key (stress indicator).
*   **Copy-Paste Detection**: Identifying when large amounts are pasted from external coaching sources.

### 2. Physical Sensor Layer (Mobile SDK)
*   **Tremor Detection**: Using the Gyroscope to detect hand-shaking associated with fear.
*   **Proximity Sensing**: Proving the phone is at the ear without needing call logs.
*   **Phone Orientation**: Detecting pacing or erratic movement during the payment process.

### 3. Contextual & Environmental Layer
*   **Screen Switching**: Tracking if the user toggles between the UPI app and WhatsApp/Instructional apps.
*   **Ambient Audio Analysis**: (Optional/Opt-in) Detecting background "Police/Authority" sounds or coaching voices.

---

## 🎨 Brand Identity

To project trust and authority, Sudharshan-AI uses a **Royal & Professional** palette:

*   🔵 **Royal Blue (`#1e40af`)**: Used for primary actions and authority elements.
*   ⚪ **Slate White (`#f8fafc`)**: Used for background and clarity.
*   🟡 **Gold Highlight (`#d4af37`)**: Used for critical alerts and brand flourishes.

---

## 🔐 Privacy Commitment
Sudharshan-AI follows a strictly **PII-Free** architecture. We do not store:
*   Usernames or phone numbers.
*   Recipient PII.
*   Raw keystrokes (only the *timing* of keystrokes is processed).

"We protect the human, not just the money."
