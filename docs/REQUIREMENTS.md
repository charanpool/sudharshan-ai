# Sudharshan-AI: Requirements Specification

**Version:** 1.0  
**Date:** January 23, 2026  
**Project:** Sudharshan-AI - Real-Time Fraud Sentinel for UPI Ecosystem  
**Hackathon:** AI for Bharat (AWS + Hack2Skill)

---

## 1. Executive Summary

Sudharshan-AI is a real-time, privacy-first fraud prevention system designed to detect psychological coercion during UPI transactions. The system intervenes **before** funds leave the victim's account, addressing the critical gap in current reactive fraud detection systems.

**Target Problem:** "Digital Arrest" scams where victims are psychologically manipulated into transferring money while on a call with scammers impersonating authorities.

**Key Statistic:** India lost ₹1,750 crore to cyber fraud in H1 2024, with 7.4 lakh complaints filed to NCRP.

---

## 2. Functional Requirements

### 2.1 Core Features (MVP)

| ID | Feature | Description | Priority |
|----|---------|-------------|----------|
| FR-01 | Agentic Fraud-Script Analysis | Analyze transaction context against known scam patterns using Bedrock Agents | P0 |
| FR-02 | Silent Circuit Breaker | Hold/delay suspicious transactions without alerting the scammer | P0 |
| FR-03 | Behavioral Biometrics | Detect anomalies in typing patterns, navigation flow, and interaction timing | P0 |
| FR-04 | Duress PIN | Secret PIN that triggers silent alert to authorities/family | P1 |
| FR-05 | Risk Dashboard | Real-time visualization of risk scores and transaction status | P1 |

### 2.2 Feature Details

#### FR-01: Agentic Fraud-Script Analysis
- **Input:** Transaction metadata, user session context, behavioral signals
- **Processing:** Bedrock Agent queries knowledge base of known scam scripts and patterns
- **Output:** Risk score (0-100) with reasoning explanation
- **Latency Target:** < 500ms

#### FR-02: Silent Circuit Breaker
- **Trigger:** Risk score ≥ 70
- **Actions:**
  - Score < 30: Approve transaction
  - Score 30-69: Add cooling period (5 minutes)
  - Score ≥ 70: Hold transaction + silent alert
- **Key Requirement:** Scammer must NOT be alerted that intervention occurred

#### FR-03: Behavioral Biometrics
- **Signals Captured:**
  - Typing speed and rhythm variations
  - Hesitation patterns (pauses before confirming)
  - Touch pressure anomalies (if available)
  - Navigation flow deviations from baseline
- **Baseline:** Established per-user over first 10-20 transactions

#### FR-04: Duress PIN
- **Setup:** User configures a secondary PIN during onboarding
- **Trigger:** Entering duress PIN instead of regular PIN
- **Action:** Transaction appears to proceed normally but triggers silent alert
- **Recipients:** Pre-configured trusted contacts, optionally authorities

#### FR-05: Risk Dashboard
- **Users:** Bank fraud analysts, compliance teams
- **Features:**
  - Real-time transaction risk feed
  - Historical pattern analysis
  - Alert management interface
  - Reporting and analytics

### 2.3 Future Roadmap Features

| ID | Feature | Phase | Description |
|----|---------|-------|-------------|
| FR-06 | Voice Sentiment Analysis | Phase 2 | Detect stress/coercion in voice during calls |
| FR-07 | On-Device Edge AI | Phase 3 | Offline protection using TensorFlow Lite |
| FR-08 | NCRP 1930 Integration | Phase 2 | Direct alert channel to cyber crime helpline |
| FR-09 | Multi-language Support | Phase 2 | Support for 10+ Indian languages |

---

## 3. Technical Requirements

### 3.1 Performance Requirements

| Metric | Target | Rationale |
|--------|--------|-----------|
| API Latency (p99) | < 1 second | Must not noticeably delay UPI transaction |
| Availability | 99.9% | Critical financial infrastructure |
| Throughput | 1,000 TPS | Support pilot bank transaction volume |
| Risk Scoring Latency | < 500ms | Real-time decision making |

### 3.2 Scalability Requirements

- **Horizontal Scaling:** Lambda functions auto-scale based on demand
- **Database:** DynamoDB on-demand capacity for unpredictable traffic patterns
- **Region:** us-east-1 (cost optimization), with future multi-region for production

### 3.3 Integration Requirements

| Integration Point | Protocol | Description |
|-------------------|----------|-------------|
| UPI App SDK | REST/HTTPS | Mobile SDK sends behavioral signals |
| Bank Core Systems | REST API | Transaction hold/release commands |
| Alert Systems | SNS/Webhook | Notifications to stakeholders |
| Dashboard | Static Web (S3) | React-based analytics interface |

### 3.4 AWS Services Required

| Service | Purpose | Free Tier Coverage |
|---------|---------|-------------------|
| Amazon Bedrock (Claude Haiku) | Fast fraud classification | Pay-per-use (~$0.25/1M tokens) |
| Amazon Bedrock Agents | Agentic RAG for scam patterns | Pay-per-use |
| Amazon Bedrock Knowledge Bases | Scam script repository | Included with Bedrock |
| AWS Lambda | Serverless compute | 1M requests/month free |
| Amazon DynamoDB | Session state, risk profiles | 25GB free |
| AWS Step Functions | Circuit breaker orchestration | 4K transitions/month free |
| Amazon API Gateway | REST API endpoints | 1M calls/month free |
| Amazon S3 | Dashboard hosting, logs | 5GB free |
| Amazon SNS | Alert notifications | 1M publishes free |
| Amazon CloudWatch | Logging and monitoring | Basic tier free |

**Estimated Prototype Cost:** $15-30 (with Free Tier benefits)

---

## 4. Security Requirements

### 4.1 Data Protection

| Requirement | Implementation |
|-------------|----------------|
| Data Encryption at Rest | DynamoDB encryption, S3 SSE |
| Data Encryption in Transit | TLS 1.3 for all API calls |
| No Raw Audio Storage | Voice analysis (Phase 2) processes on-device only |
| PII Minimization | Store behavioral hashes, not raw biometric data |

### 4.2 Access Control

- **API Authentication:** API Gateway with API keys + IAM
- **Dashboard Access:** Cognito User Pools with MFA
- **Service-to-Service:** IAM roles with least privilege

### 4.3 Audit & Compliance

- All API calls logged to CloudWatch
- Transaction decisions logged with reasoning (explainability)
- 90-day log retention for audit purposes

---

## 5. Compliance Requirements

### 5.1 DPDP Act 2023 (Digital Personal Data Protection)

| Requirement | How Sudharshan-AI Complies |
|-------------|---------------------------|
| Purpose Limitation | Data used only for fraud prevention |
| Data Minimization | Behavioral signals only, no raw audio/video |
| Consent | Integrated into UPI app T&C |
| Right to Erasure | User baseline data deletable on request |
| Data Localization | All processing in AWS India region (production) |

### 5.2 RBI Guidelines

| Guideline | Compliance Approach |
|-----------|---------------------|
| Real-time Fraud Prevention | Core system capability |
| Customer Notification | Silent for scammer, transparent to customer post-event |
| Grievance Redressal | Dashboard provides audit trail for disputes |

### 5.3 NPCI/UPI Standards

- Compatible with UPI 2.0 transaction flow
- Non-blocking integration (advisory, not mandatory hold)
- Pilot mode: Banks retain final decision authority

---

## 6. User Experience Requirements

### 6.1 Victim Experience
- **Invisible Protection:** No additional steps for legitimate transactions
- **Graceful Intervention:** Cooling period feels like "processing delay"
- **Post-Event Transparency:** Notification explaining why transaction was reviewed

### 6.2 False Positive Handling
- Soft interventions (delay) before hard blocks
- User can override with biometric confirmation
- Trusted contacts whitelist for recurring payments
- Feedback loop to improve model accuracy

### 6.3 Accessibility
- Designed for 250M+ non-English speaking users
- Simple, clear messaging in regional languages (Phase 2)
- Voice-based confirmation options (Phase 2)

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Detection Rate | > 80% of coercion-based frauds | True positives / Total fraud attempts |
| False Positive Rate | < 5% | Legitimate transactions flagged |
| MTTC (Mean Time to Contain) | < 1 second | Time from detection to intervention |
| User Satisfaction | > 4.0/5.0 | Post-intervention survey |
| Cost per Transaction | < ₹0.10 | Total AWS cost / Transactions processed |

---

## 8. Assumptions & Constraints

### Assumptions
1. UPI apps will integrate the Sudharshan SDK
2. Banks will implement transaction hold APIs
3. Users consent to behavioral monitoring via app T&C
4. Bedrock credits available for prototype phase

### Constraints
1. **Budget:** $30-40 total for prototype
2. **Timeline:** MVP by February 22, 2026
3. **Team Size:** Solo developer
4. **No access to real transaction data:** Using synthetic data for demo

---

## 9. Glossary

| Term | Definition |
|------|------------|
| Digital Arrest | Scam where victims are manipulated by fake authority figures |
| Golden Hour | Critical window (1-4 hours) before stolen funds are laundered |
| Agentic RAG | AI agent that reasons over retrieved documents |
| Circuit Breaker | Pattern that stops cascading failures; here, stops fraudulent transactions |
| Duress PIN | Secret PIN indicating user is under coercion |
| MTTC | Mean Time To Contain - time from detection to intervention |

---

*Document prepared for AI for Bharat Hackathon (AWS + Hack2Skill)*
