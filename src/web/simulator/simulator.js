// Simulator Logic
let keystrokes = [];
let lastKeyTime = 0;
let hesitations = 0;
const HESITATION_THRESHOLD = 2000; // 2 seconds

const amountInput = document.getElementById('amount-input');
const payBtn = document.getElementById('pay-btn');
const riskModal = document.getElementById('risk-modal');
const riskCircle = document.getElementById('risk-circle');
const riskValue = document.getElementById('risk-value');
const riskTitle = document.getElementById('risk-title');
const riskReason = document.getElementById('risk-reason');
const aiThought = document.getElementById('ai-thought');

// Tracking inputs
amountInput.addEventListener('keydown', (e) => {
    const now = Date.now();
    if (lastKeyTime > 0) {
        const interval = now - lastKeyTime;
        keystrokes.push(interval);
        if (interval > HESITATION_THRESHOLD) {
            hesitations++;
            updateTelemetry();
        }
    }
    lastKeyTime = now;
    updateTelemetry();
});

function calculateWPM() {
    if (keystrokes.length < 2) return 0;
    const totalTimeMinutes = (keystrokes.reduce((a, b) => a + b, 0)) / 60000;
    return Math.round((keystrokes.length / 5) / totalTimeMinutes) || 0;
}

function calculateVariance() {
    if (keystrokes.length < 2) return 0;
    const mean = keystrokes.reduce((a, b) => a + b, 0) / keystrokes.length;
    const sqDiff = keystrokes.map(k => Math.pow(k - mean, 2));
    const variance = sqDiff.reduce((a, b) => a + b, 0) / keystrokes.length;
    return Math.round(variance);
}

function updateTelemetry() {
    document.getElementById('stat-wpm').innerText = calculateWPM();
    document.getElementById('stat-hesitations').innerText = hesitations;
    document.getElementById('stat-variance').innerText = calculateVariance();
}

payBtn.addEventListener('click', async () => {
    // Show loading
    riskModal.classList.remove('hidden');
    riskTitle.innerText = "Analyzing Risk...";
    riskReason.innerText = "Sudharshan-AI is checking transaction safety.";

    const payload = {
        session_id: "sim-" + Math.random().toString(36).substr(2, 9),
        user_id: "judge-1",
        signals: {
            typing_speed_wpm: calculateWPM(),
            hesitation_count: hesitations,
            time_on_confirm_screen_ms: keystrokes.reduce((a, b) => a + b, 0),
            is_on_call: document.getElementById('on-call-toggle').checked,
            time_of_day_hour: new Date().getHours()
        },
        transaction: {
            amount: parseFloat(amountInput.value) || 0,
            recipient_type: "new",
            recipient_id: "sanjeev.cbi@upi"
        }
    };

    aiThought.innerText = "Transmitting behavioral signals to Bedrock (Claude Haiku)...";

    // Simulate API Call (Replace with actual endpoint after deployment)
    try {
        // For prototype demo without live backend yet, we'll simulate the response
        // In a real demo, we'd fetch(API_URL, { method: 'POST', ... })
        setTimeout(() => {
            const risk = calculateSimulatedRisk(payload);
            updateRiskUI(risk);
        }, 2000);
    } catch (e) {
        console.error(e);
    }
});

function calculateSimulatedRisk(payload) {
    let score = 10;
    if (payload.signals.is_on_call) score += 40;
    if (payload.transaction.amount > 50000) score += 20;
    if (payload.signals.hesitation_count > 3) score += 20;

    let reason = "Transaction appears safe.";
    if (score > 70) {
        reason = "High likelihood of Digital Arrest scam. User is on a call while transferring a large amount with high hesitation.";
    } else if (score > 30) {
        reason = "Unfavorable conditions detected. Transaction delayed for 5 minutes for your safety.";
    }

    return { score, reason };
}

function updateRiskUI(risk) {
    const color = risk.score > 70 ? '#ef4444' : (risk.score > 30 ? '#f59e0b' : '#10b981');

    // Update Ring
    riskCircle.style.stroke = color;
    riskCircle.style.strokeDasharray = `${risk.score}, 100`;

    // Update Text with counter animation
    let current = 0;
    const interval = setInterval(() => {
        if (current >= risk.score) {
            clearInterval(interval);
            riskValue.innerText = `${risk.score}%`;
        } else {
            current++;
            riskValue.innerText = `${current}%`;
        }
    }, 10);

    riskTitle.innerText = risk.score > 70 ? "SHIELD ACTIVATED" : (risk.score > 30 ? "CAUTION" : "SAFE");
    riskTitle.style.color = color;
    riskReason.innerText = risk.reason;
    aiThought.innerHTML = `<span style="color: ${color}">●</span> Bedrock reasoning: ${risk.reason}`;
}

document.getElementById('modal-close').addEventListener('click', () => {
    riskModal.classList.add('hidden');
});
