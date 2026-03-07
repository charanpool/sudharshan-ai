# Sudharshan-AI: System Design Document

**Version:** 1.0  
**Date:** January 23, 2026  
**Project:** Sudharshan-AI - Real-Time Fraud Sentinel for UPI Ecosystem  
**Hackathon:** AI for Bharat (AWS + Hack2Skill)

---

## 1. Overview

### 1.1 System Purpose

Sudharshan-AI is a real-time fraud prevention layer that detects psychological coercion during UPI transactions. Unlike traditional rule-based systems that react after fraud occurs, Sudharshan-AI intervenes **before** funds leave the victim's account.

### 1.2 Design Principles

| Principle | Application |
|-----------|-------------|
| **Privacy-First** | Behavioral signals only; no raw audio/video stored |
| **Serverless** | Lambda-based for cost efficiency and auto-scaling |
| **Sub-Second Response** | All decisions within 1 second |
| **Explainable AI** | Every risk score includes reasoning |
| **Graceful Degradation** | System fails open (allows transaction) if unavailable |

### 1.3 Key Differentiators

```
┌─────────────────────────────────────────────────────────────────┐
│                    CURRENT SYSTEMS                              │
│  User → Transaction → Bank Rules → Approve/Deny → Report Fraud │
│                                                    (Too Late)   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    SUDHARSHAN-AI                                │
│  User → Behavioral Analysis → AI Risk Score → Intervene BEFORE  │
│         (While on scam call)                   Transaction      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌──────────────┐     HTTPS      ┌──────────────┐
│   UPI App    │ ──────────────▶│ API Gateway  │
│   (SDK)      │                └──────┬───────┘
└──────────────┘                       │
                                       ▼
                              ┌────────────────┐
                              │    Lambda      │
                              │ Risk Analyzer  │
                              └────────┬───────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌────────────┐    ┌────────────────┐   ┌─────────────┐
           │  DynamoDB  │    │ Bedrock Agent  │   │    Step     │
           │  Session   │    │ (Claude Haiku) │   │  Functions  │
           └────────────┘    └────────────────┘   └─────────────┘
                                    │                    │
                                    ▼                    ▼
                             ┌────────────┐       ┌───────────┐
                             │ Knowledge  │       │    SNS    │
                             │    Base    │       │  Alerts   │
                             │  (S3)      │       └───────────┘
                             └────────────┘
```

### 2.2 Component Diagram

See `docs/diagrams/architecture.png` for the detailed AWS architecture diagram.

---

## 3. AWS Service Justification

### 3.1 Why These Services?

| Service | Why Chosen | Alternatives Considered |
|---------|------------|------------------------|
| **Amazon Bedrock (Claude Haiku)** | Fast, cheap inference (~100ms); understands context and nuance | SageMaker (too complex), OpenAI (not AWS-native) |
| **Bedrock Agents** | Native agentic RAG; handles multi-step reasoning | Custom LangChain (more code to maintain) |
| **AWS Lambda** | Serverless = pay only when used; auto-scales | ECS/Fargate (overkill for this use case) |
| **DynamoDB** | Single-digit ms latency; scales automatically | RDS (higher cost, needs provisioning) |
| **Step Functions** | Visual workflow; built-in retry/error handling | Custom orchestration (error-prone) |
| **API Gateway** | Managed REST API; integrates with Lambda | ALB (need always-on compute) |
| **S3** | Cheap static hosting; stores knowledge base | CloudFront alone (still needs origin) |
| **SNS** | Fan-out alerts to multiple channels | SQS (point-to-point, not fan-out) |

### 3.2 Cost Optimization Strategy

| Strategy | Implementation |
|----------|----------------|
| **Use Free Tier** | Lambda, DynamoDB, Step Functions, API Gateway, S3, SNS |
| **Haiku over Sonnet** | 10x cheaper; sufficient for classification tasks |
| **On-Demand DynamoDB** | No provisioned capacity; pay per request |
| **us-east-1 Region** | 10-15% cheaper than ap-south-1 |
| **Minimal Bedrock Calls** | Cache repeated queries; batch where possible |

**Estimated Monthly Cost (Prototype):** $15-30

---

## 4. Data Flow

### 4.1 Transaction Analysis Flow

```
1. USER ACTION
   └─▶ User opens UPI app, initiates transaction

2. SDK CAPTURE (Client-side)
   └─▶ Captures: typing patterns, timing, navigation flow
   └─▶ Sends to API Gateway (HTTPS)

3. RISK ANALYSIS (Lambda: Risk Analyzer)
   └─▶ Retrieves user baseline from DynamoDB
   └─▶ Computes behavioral deviation score
   └─▶ Enriches with transaction context

4. AI INFERENCE (Bedrock Agent)
   └─▶ Queries Knowledge Base for matching scam patterns
   └─▶ Reasons through transaction context
   └─▶ Returns risk score (0-100) + explanation

5. DECISION (Lambda → Step Functions)
   └─▶ Score < 30: APPROVE → Return to SDK
   └─▶ Score 30-69: DELAY → Add 5-min cooling period
   └─▶ Score ≥ 70: HOLD → Trigger Circuit Breaker

6. CIRCUIT BREAKER (Step Functions)
   └─▶ Hold transaction in pending state
   └─▶ Send silent alert via SNS
   └─▶ Wait for manual review or timeout

7. RESPONSE TO USER
   └─▶ Low risk: Transaction proceeds normally
   └─▶ Medium risk: "Processing, please wait..."
   └─▶ High risk: "Transaction under review" (no scammer alert)
```

### 4.2 Sequence Diagram

See `docs/diagrams/process-flow.png` for the detailed process flow diagram.

---

## 5. Component Design

### 5.1 Mobile SDK (Client-Side)

**Responsibilities:**
- Capture behavioral signals (typing, timing, navigation)
- Send signals to API Gateway
- Display intervention messages

**Technology:** React Native / Native iOS & Android

**Data Captured:**
```json
{
  "session_id": "uuid",
  "user_id": "hashed_user_id",
  "signals": {
    "typing_speed_wpm": 45,
    "typing_rhythm_variance": 0.3,
    "hesitation_count": 5,
    "time_on_confirm_screen_ms": 8500,
    "navigation_path": ["home", "send", "amount", "confirm"],
    "device_motion": "stable"
  },
  "transaction": {
    "amount": 50000,
    "recipient_type": "new",
    "time_of_day": "02:30"
  }
}
```

### 5.2 API Gateway

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze` | Submit transaction for risk analysis |
| POST | `/duress` | Trigger duress alert |
| GET | `/status/{txn_id}` | Check transaction status |
| POST | `/feedback` | Submit false positive feedback |

**Security:**
- API Key authentication
- Rate limiting: 100 req/sec per user
- Request validation with JSON Schema

### 5.3 Lambda: Risk Analyzer

**Responsibilities:**
- Receive behavioral signals from SDK
- Fetch user baseline from DynamoDB
- Calculate behavioral deviation score
- Call Bedrock Agent for AI analysis
- Return combined risk score

**Code Structure:**
```
lambda/
├── risk_analyzer/
│   ├── handler.py          # Main Lambda orchestrator
│   ├── core/               # Core logic engines
│   │   ├── analyzer.py     # Bedrock AI integration
│   │   └── behavioral.py   # Behavioral analysis logic
│   ├── utils/              # Supporting utilities
│   │   ├── models.py       # Data models
│   │   └── reporting.py    # Investigator report logic
│   └── scam_intelligence.json # Scam script intelligence
```

**Timeout:** 10 seconds  
**Memory:** 512 MB  
**Concurrency:** Auto-scale (no reserved)

### 5.4 Lambda: Behavioral Engine

**Responsibilities:**
- Compute typing pattern deviation
- Detect hesitation anomalies
- Compare against user baseline
- Update baseline with new data points

**Algorithm (Simplified):**
```python
def compute_behavioral_score(current_signals, baseline):
    deviations = []
    
    # Typing speed deviation
    typing_dev = abs(current_signals.typing_speed - baseline.avg_typing_speed)
    typing_dev_normalized = typing_dev / baseline.std_typing_speed
    deviations.append(typing_dev_normalized)
    
    # Hesitation deviation
    hesitation_dev = current_signals.hesitation_count - baseline.avg_hesitations
    deviations.append(max(0, hesitation_dev))
    
    # Time on confirm screen
    if current_signals.time_on_confirm > baseline.avg_confirm_time * 2:
        deviations.append(2.0)  # Significant deviation
    
    # Weighted average
    return min(100, sum(deviations) * 15)
```

### 5.5 Bedrock Agent: Fraud Script Analyzer

**Agent Configuration:**
- **Model:** Claude 3 Haiku
- **Knowledge Base:** S3 bucket with scam script patterns
- **Instructions:**

```
You are a fraud detection agent analyzing UPI transactions for signs of 
psychological coercion. You have access to a knowledge base of known scam 
patterns including "Digital Arrest" scripts, lottery scams, and KYC fraud.

Given transaction context and behavioral signals, determine:
1. Does this match any known scam pattern?
2. What is the likelihood (0-100) that the user is being coerced?
3. Provide a brief explanation of your reasoning.

Be conservative: False negatives (missing fraud) are worse than false 
positives (flagging legitimate transactions).
```

**Knowledge Base Contents:**
- Digital arrest scam scripts (IRS, Police, CBI impersonation)
- Lottery/prize scam patterns
- KYC update fraud patterns
- Investment scam indicators
- Relationship scam markers

### 5.6 Step Functions: Silent Circuit Breaker

**State Machine:**

```
┌─────────────────┐
│   Start         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evaluate Risk  │
└────────┬────────┘
         │
    ┌────┴────┬─────────────┐
    │         │             │
    ▼         ▼             ▼
┌───────┐ ┌────────┐  ┌──────────┐
│Approve│ │ Delay  │  │   Hold   │
│       │ │ 5 min  │  │          │
└───┬───┘ └────┬───┘  └────┬─────┘
    │          │           │
    │          │           ▼
    │          │     ┌──────────┐
    │          │     │Send Alert│
    │          │     └────┬─────┘
    │          │          │
    │          │          ▼
    │          │     ┌──────────┐
    │          │     │Wait Review│
    │          │     │ (30 min) │
    │          │     └────┬─────┘
    │          │          │
    └────┬─────┴──────────┘
         │
         ▼
┌─────────────────┐
│   End           │
└─────────────────┘
```

### 5.7 DynamoDB Tables

**Table: UserBaselines**
```
PK: user_id
Attributes:
  - avg_typing_speed: Number
  - std_typing_speed: Number
  - avg_hesitations: Number
  - avg_confirm_time: Number
  - transaction_count: Number
  - last_updated: Timestamp
```

**Table: Sessions**
```
PK: session_id
SK: timestamp
Attributes:
  - user_id: String
  - signals: Map
  - risk_score: Number
  - decision: String (approve/delay/hold)
  - ttl: Number (24 hours)
```

**Table: RiskProfiles**
```
PK: user_id
Attributes:
  - trusted_recipients: List
  - duress_pin_hash: String
  - alert_contacts: List
  - risk_tolerance: String (low/medium/high)
```

### 5.8 S3 Buckets

| Bucket | Purpose | Access |
|--------|---------|--------|
| `sudharshan-knowledge-base` | Scam script patterns for RAG | Bedrock Agent only |
| `sudharshan-dashboard` | Static web hosting | Public (CloudFront) |
| `sudharshan-logs` | Audit logs | Private, encrypted |

---

## 6. Security Design

### 6.1 Data Protection

```
┌─────────────────────────────────────────────────────┐
│                   DATA FLOW                         │
├─────────────────────────────────────────────────────┤
│  Mobile SDK ──TLS 1.3──▶ API Gateway                │
│                              │                      │
│                         IAM Role                    │
│                              │                      │
│                              ▼                      │
│                         Lambda                      │
│                              │                      │
│                     ┌────────┴────────┐             │
│                     ▼                 ▼             │
│              DynamoDB (SSE)    Bedrock (SSE)        │
└─────────────────────────────────────────────────────┘
```

### 6.2 IAM Roles

| Role | Permissions |
|------|-------------|
| `SudharshanApiRole` | API Gateway invoke Lambda |
| `SudharshanLambdaRole` | DynamoDB CRUD, Bedrock invoke, SNS publish |
| `SudharshanStepRole` | Lambda invoke, SNS publish |
| `SudharshanDashboardRole` | Read-only DynamoDB, CloudWatch |

### 6.3 Secrets Management

- API keys stored in AWS Secrets Manager
- No hardcoded credentials
- Rotation policy: 90 days

---

## 7. Monitoring & Observability

### 7.1 CloudWatch Metrics

| Metric | Alarm Threshold |
|--------|-----------------|
| API Latency p99 | > 1000ms |
| Lambda Errors | > 1% |
| Risk Score Avg | > 50 (anomaly) |
| DynamoDB Throttles | > 0 |

### 7.2 Logging Strategy

```
Log Format (JSON):
{
  "timestamp": "2026-01-23T10:30:00Z",
  "request_id": "uuid",
  "user_id": "hashed",
  "action": "analyze",
  "risk_score": 75,
  "decision": "hold",
  "reasoning": "Matches digital arrest pattern",
  "latency_ms": 450
}
```

### 7.3 Dashboard Metrics

- Transactions analyzed per hour
- Risk score distribution
- Intervention rate
- False positive rate (from feedback)

---

## 8. Deployment Strategy

### 8.1 Infrastructure as Code

**Tool:** AWS CDK (TypeScript) or SAM

**Stack Structure:**
```
infrastructure/
├── lib/
│   ├── api-stack.ts        # API Gateway + Lambda
│   ├── data-stack.ts       # DynamoDB tables
│   ├── ai-stack.ts         # Bedrock Agent + KB
│   ├── workflow-stack.ts   # Step Functions
│   └── monitoring-stack.ts # CloudWatch
├── bin/
│   └── app.ts
└── cdk.json
```

### 8.2 Deployment Stages

| Stage | Environment | Purpose |
|-------|-------------|---------|
| Dev | us-east-1 | Development + testing |
| Demo | us-east-1 | Hackathon demo |
| Prod | ap-south-1 | Production (future) |

### 8.3 CI/CD Pipeline (Future)

```
GitHub Push → CodePipeline → CodeBuild → CDK Deploy → CloudFormation
```

---

## 9. Testing Strategy

### 9.1 Test Types

| Type | Tool | Coverage |
|------|------|----------|
| Unit Tests | pytest | Lambda functions |
| Integration Tests | pytest + moto | AWS service mocks |
| Load Tests | Locust | API Gateway endpoints |
| E2E Tests | Manual | Full flow demo |

### 9.2 Test Scenarios

1. **Normal Transaction:** Low risk score, approved
2. **Suspicious Timing:** Medium risk, delayed
3. **High Risk Pattern:** High risk, held + alert
4. **Duress PIN:** Alert triggered, fake approval
5. **Baseline Learning:** New user, baseline established

---

## 10. Future Enhancements

### Phase 2 (Q2 2026)
- Voice sentiment analysis (on-device)
- NCRP 1930 integration
- Multi-language support

### Phase 3 (Q3 2026)
- Edge AI with TensorFlow Lite
- Nitro Enclaves for enterprise
- B2B pilot with regional banks

---

## 11. Appendix

### A. API Request/Response Examples

**POST /analyze**
```json
// Request
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "hash_abc123",
  "signals": {
    "typing_speed_wpm": 25,
    "hesitation_count": 8,
    "time_on_confirm_ms": 15000
  },
  "transaction": {
    "amount": 100000,
    "recipient": "new_upi@bank"
  }
}

// Response
{
  "risk_score": 78,
  "decision": "hold",
  "reasoning": "Abnormal hesitation pattern combined with large amount to new recipient at unusual hour",
  "transaction_id": "txn_xyz789"
}
```

### B. Knowledge Base Sample Entry

```json
{
  "pattern_id": "digital_arrest_001",
  "name": "Digital Arrest - Police Impersonation",
  "indicators": [
    "Claim of arrest warrant",
    "Demand for immediate payment",
    "Threat of public embarrassment",
    "Request to stay on video call",
    "Isolation from family members"
  ],
  "typical_amounts": [50000, 100000, 200000],
  "time_patterns": ["late_night", "early_morning"],
  "risk_weight": 0.9
}
```

---

*Document prepared for AI for Bharat Hackathon (AWS + Hack2Skill)*
