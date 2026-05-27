// STATE MANAGEMENT
let selectedCandidateId = null;
let isAuthenticated = false;
let isSubmitting = false;

// CANDIDATE DATA
const candidatesData = {
    1: {
        name: "Nakul Narang",
        party: "Independent Party",
        symbol: "🌟",
        emoji: "👨‍💼",
        age: 45,
        education: "MBA, Harvard Business School",
        experience: "15 years",
        achievements: [
            "Implemented 50+ schools in rural areas",
            "Launched free healthcare program for 100,000 families",
            "Championed gender equality legislation"
        ],
        vision: "Building an inclusive society with focus on education, healthcare, and gender equality.",
        contact: "nakul@independentparty.com"
    },
    2: {
        name: "Shristy Suhane",
        party: "Progressive Alliance",
        symbol: "🌱",
        emoji: "👩‍💼",
        age: 42,
        education: "PhD in Environmental Science",
        experience: "20 years",
        achievements: [
            "Planted 1 million trees across the state",
            "Reduced carbon emissions by 30%",
            "Established 20 wildlife sanctuaries"
        ],
        vision: "Creating a sustainable future through environmental protection and social justice.",
        contact: "shristy@progressivealliance.com"
    },
    3: {
        name: "Richa Singh",
        party: "Democratic Party",
        symbol: "💼",
        emoji: "👨‍💼",
        age: 48,
        education: "MS in Economics, Stanford",
        experience: "20 years",
        achievements: [
            "Created 500,000+ jobs",
            "Increased GDP growth by 8%",
            "Established 100+ business centers"
        ],
        vision: "Driving economic prosperity through job creation and business development.",
        contact: "richa@democraticparty.com"
    },
    4: {
        name: "Palak Vishwakarma",
        party: "Republican Party",
        symbol: "🛡️",
        emoji: "👩‍💼",
        age: 50,
        education: "MS in Civil Engineering, MIT",
        experience: "25 years",
        achievements: [
            "Built 5000+ km of highways",
            "Modernized defense systems",
            "Developed 15 smart cities"
        ],
        vision: "Strengthening national security and building world-class infrastructure.",
        contact: "palak@republicanparty.com"
    }
};
// Chart colours matching CSS variables
const CHART_COLORS = {
    1: '#1a2744',
    2: '#046A38',
    3: '#FF671F',
    4: '#C6962A'
};

// In-memory vote store  { candidateId: count }
const voteStore = {};

// PAGE NAVIGATION
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    clearErrors();
    if (pageId !== 'votingPage') {
        resetCandidateSelection();
    }
}

// ERROR HANDLING 
function clearErrors() {
    document.querySelectorAll('.error').forEach(error => {
        error.classList.remove('show');
        error.textContent = '';
    });
}

function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}

// SIGNUP
document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const voterId = document.getElementById('signupVoterId').value.trim();
    const password = document.getElementById('signupPassword').value;
    const btn = e.target.querySelector('.btn-primary');
    const originalText = btn.textContent;

    btn.textContent = '⏳ Creating Account...';
    btn.disabled = true;

    // Validation
    if (!name || !email || !password) {
        showError('signupError', '⚠️ Please fill in all required fields');
        resetButton(btn, originalText);
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('signupError', '⚠️ Please enter a valid email address');
        resetButton(btn, originalText);
        return;
    }

    if (password.length < 6) {
        showError('signupError', '⚠️ Password must be at least 6 characters');
        resetButton(btn, originalText);
        return;
    }

    // Voter ID is optional; only validate if provided
    if (voterId && voterId.length < 5) {
        showError('signupError', '⚠️ Please enter a valid Voter ID (at least 5 characters)');
        resetButton(btn, originalText);
        return;
    }

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    isAuthenticated = true;
    btn.textContent = '✓ Account Created!';

    setTimeout(() => {
        resetButton(btn, originalText);
        this.reset();
        showPage('votingPage');
    }, 800);
});

// LOGIN
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    const btn = e.target.querySelector('.btn-primary');
    const originalText = btn.textContent;

    btn.textContent = '⏳ Signing In...';
    btn.disabled = true;

    // Validation
    if (!email || !password) {
        showError('loginError', '⚠️ Please fill in all fields');
        resetButton(btn, originalText);
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('loginError', '⚠️ Please enter a valid email address');
        resetButton(btn, originalText);
        return;
    }

    if (password.length < 6) {
        showError('loginError', '⚠️ Password must be at least 6 characters');
        resetButton(btn, originalText);
        return;
    }

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));

    isAuthenticated = true;
    btn.textContent = '✓ Welcome Back!';

    setTimeout(() => {
        resetButton(btn, originalText);
        this.reset();
        showPage('votingPage');
    }, 800);
});

// CANDIDATE SELECTION
function selectCandidate(candidateId) {
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.classList.remove('selected');
    });

    const selectedCard = document.getElementById(`candidate${candidateId}`).closest('.candidate-card');
    if (selectedCard) {
        selectedCard.classList.add('selected');
        selectedCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    selectedCandidateId = candidateId;
    console.log(`✓ Candidate ${candidateId} selected`);
}

function resetCandidateSelection() {
    document.querySelectorAll('input[name="candidate"]').forEach(radio => {
        radio.checked = false;
    });
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.classList.remove('selected');
    });
    selectedCandidateId = null;
}

// CANDIDATE INFO MODAL
function showCandidateInfo(event, candidateId) {
    event.preventDefault();
    event.stopPropagation();

    const candidate = candidatesData[candidateId];
    if (!candidate) return;

    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.innerHTML = `
        <div class="modal">
            <button class="modal-close" onclick="this.closest('.modal-backdrop').remove()">×</button>
            
            <div class="modal-header">
                <div class="modal-symbol">${candidate.symbol}</div>
                <h2>${candidate.emoji} ${candidate.name}</h2>
                <span class="modal-badge">${candidate.party}</span>
            </div>

            <div class="modal-info">
                <div class="info-box">
                    <div class="info-label">Age</div>
                    <div class="info-value">${candidate.age} years</div>
                </div>
                <div class="info-box">
                    <div class="info-label">Experience</div>
                    <div class="info-value">${candidate.experience}</div>
                </div>
            </div>

            <div class="modal-section">
                <h3>📚 Education</h3>
                <p>${candidate.education}</p>
            </div>

            <div class="modal-section">
                <h3>🏆 Key Achievements</h3>
                <ul class="achievements-list">
                    ${candidate.achievements.map(a => `<li>✓ ${a}</li>`).join('')}
                </ul>
            </div>

            <div class="modal-section">
                <h3>🎯 Vision</h3>
                <p>${candidate.vision}</p>
            </div>

            <div class="modal-section">
                <h3>📧 Contact</h3>
                <p>${candidate.contact}</p>
            </div>

            <button class="btn btn-primary" onclick="this.closest('.modal-backdrop').remove()">Close</button>
        </div>
    `;

    backdrop.addEventListener('click', function(e) {
        if (e.target === backdrop) {
            backdrop.remove();
        }
    });

    // Close on ESC key
    const handleEsc = function(e) {
        if (e.key === 'Escape') {
            backdrop.remove();
            document.removeEventListener('keydown', handleEsc);
        }
    };
    document.addEventListener('keydown', handleEsc);

    document.body.appendChild(backdrop);
}

// VOTE SUBMISSION
async function submitVote() {
    if (!selectedCandidateId) {
        showCustomAlert('⚠️ Please Select a Candidate', 'You must select a candidate before submitting your vote.');
        return;
    }

    if (!isAuthenticated) {
        showCustomAlert('🔒 Authentication Required', 'Please login or sign up first.');
        setTimeout(() => showPage('signupPage'), 2000);
        return;
    }

    if (isSubmitting) return;
    isSubmitting = true;

    const btn = event.target;
    const originalText = btn.textContent;

    btn.textContent = '📝 Submitting...';
    btn.disabled = true;

    await new Promise(resolve => setTimeout(resolve, 2000));

    btn.textContent = '✓ Vote Recorded!';

    console.log('🗳️ Vote submitted successfully for candidate:', selectedCandidateId);

    createConfetti();

    setTimeout(() => {
        showPage('successPage');
        resetButton(btn, originalText);
        selectedCandidateId = null;
        isAuthenticated = false;
    }, 1500);
}

// ==================== LOGOUT ====================
function logout() {
    isAuthenticated = false;
    selectedCandidateId = null;
    document.getElementById('signupForm').reset();
    document.getElementById('loginForm').reset();
    showPage('signupPage');
    console.log('🚪 User logged out');
}

// ==================== UTILITY FUNCTIONS ====================
function resetButton(button, originalText) {
    button.textContent = originalText;
    button.disabled = false;
    isSubmitting = false;
}

function showCustomAlert(title, message) {
    const alertDiv = document.createElement('div');
    alertDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(30px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        z-index: 10000;
        max-width: 400px;
        text-align: center;
        animation: fadeInScale 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    `;

    alertDiv.innerHTML = `
        <h3 style="font-size: 20px; margin-bottom: 10px; color: white;">${title}</h3>
        <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 20px;">${message}</p>
        <button onclick="this.parentElement.remove(); document.querySelector('.alert-backdrop').remove();" style="
            padding: 12px 30px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
        ">OK</button>
    `;

    const backdrop = document.createElement('div');
    backdrop.className = 'alert-backdrop';
    backdrop.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.6);
        backdrop-filter: blur(5px);
        z-index: 9999;
        animation: fadeIn 0.3s;
    `;
    backdrop.onclick = () => {
        backdrop.remove();
        alertDiv.remove();
    };

    document.body.appendChild(backdrop);
    document.body.appendChild(alertDiv);

    setTimeout(() => {
        backdrop.remove();
        alertDiv.remove();
    }, 5000);
}

function createConfetti() {
    const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.setProperty('--x', (Math.random() * 200 - 100) + 'px');
        confetti.style.setProperty('--r', (Math.random() * 720) + 'deg');
        confetti.style.animationDuration = (2 + Math.random() * 3) + 's';
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';

        document.body.appendChild(confetti);

        setTimeout(() => confetti.remove(), 5000);
    }
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const activePage = document.querySelector('.page.active');
        if (activePage && activePage.id !== 'signupPage') {
            showPage('signupPage');
        }
    }
});

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🗳️ Premium Voting System Initialized');
    console.log('Version: 3.0.0 - Glassmorphism Edition');
    console.log('Default Landing: Signup Page');

    // Smooth scrolling
    document.documentElement.style.scrollBehavior = 'smooth';

    // Log system status
    console.log('✓ All systems operational');
});
// ==================== ADMIN LOGIN ====================
document.getElementById('adminLoginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const u = document.getElementById('adminUsername').value;
    const p = document.getElementById('adminPassword').value;
    if (u === 'sagar' && p === 'sagar123') {
        sessionStorage.setItem('role', 'admin');
        renderDashboard();
        showPage('adminDashboard');
    } else {
        showError('adminLoginError', '⚠️ Invalid admin credentials');
    }
});

function adminLogout() {
    sessionStorage.removeItem('role');
    showPage('loginPage');
}

// ==================== DASHBOARD RENDERING ====================
function renderDashboard() {
    const totalVotes = Object.values(voteStore).reduce((a, b) => a + b, 0);

    document.getElementById('totalVotes').textContent = totalVotes;
    document.getElementById('totalVoters').textContent = '—';  // extend if you track registered users
    document.getElementById('turnoutRate').textContent = totalVotes > 0 ? totalVotes : '0';

    renderBarChart(totalVotes);
    renderPieChart(totalVotes);
}

// ── BAR CHART ──
function renderBarChart(totalVotes) {
    const container = document.getElementById('barChart');
    if (totalVotes === 0) {
        container.innerHTML = '<div class="chart-empty">No votes cast yet</div>';
        return;
    }
    const maxVotes = Math.max(...Object.keys(candidatesData).map(id => voteStore[id] || 0), 1);
    container.innerHTML = Object.keys(candidatesData).map(id => {
        const c = candidatesData[id];
        const votes = voteStore[id] || 0;
        const widthPct = Math.round((votes / maxVotes) * 100);
        const color = CHART_COLORS[id];
        return `
            <div class="bar-row">
                <div class="bar-label" title="${c.name}">${c.symbol} ${c.name.split(' ')[0]}</div>
                <div class="bar-track">
                    <div class="bar-fill" style="width:${widthPct}%;background:${color};">
                        ${votes > 0 ? votes + ' vote' + (votes > 1 ? 's' : '') : ''}
                    </div>
                </div>
                <div class="bar-count">${votes}</div>
            </div>`;
    }).join('');
}

// ── PIE CHART (Canvas) ──
function renderPieChart(totalVotes) {
    const canvas = document.getElementById('pieChart');
    const legend = document.getElementById('pieLegend');
    const ctx = canvas.getContext('2d');
    const W = 200, H = 200, cx = W / 2, cy = H / 2, R = 80;
    ctx.clearRect(0, 0, W, H);

    if (totalVotes === 0) {
        // Draw empty grey ring
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.strokeStyle = '#e8edf8';
        ctx.lineWidth = 28;
        ctx.stroke();
        ctx.fillStyle = '#aab0c8';
        ctx.font = '13px Segoe UI';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No votes yet', cx, cy);
        legend.innerHTML = '';
        return;
    }

    // Build slices
    const slices = Object.keys(candidatesData).map(id => ({
        id,
        name: candidatesData[id].name,
        party: candidatesData[id].party,
        votes: voteStore[id] || 0,
        color: CHART_COLORS[id]
    })).filter(s => s.votes > 0);

    let startAngle = -Math.PI / 2;
    slices.forEach(s => {
        const sliceAngle = (s.votes / totalVotes) * Math.PI * 2;
        // Outer filled arc
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, R, startAngle, startAngle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = s.color;
        ctx.fill();
        // White separator line
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + R * Math.cos(startAngle), cy + R * Math.sin(startAngle));
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        startAngle += sliceAngle;
    });

    // White donut hole
    ctx.beginPath();
    ctx.arc(cx, cy, R * 0.52, 0, Math.PI * 2);
    ctx.fillStyle = '#f7f9fc';
    ctx.fill();

    // Centre text
    ctx.fillStyle = '#1a2744';
    ctx.font = 'bold 18px Segoe UI';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(totalVotes, cx, cy - 8);
    ctx.font = '11px Segoe UI';
    ctx.fillStyle = '#4a5568';
    ctx.fillText('total votes', cx, cy + 10);

    // Legend
    legend.innerHTML = slices.map(s => {
        const pct = Math.round((s.votes / totalVotes) * 100);
        return `
            <div class="legend-item">
                <div class="legend-dot" style="background:${s.color}"></div>
                <div>
                    <span class="legend-text">${s.party.split(' ')[0]}</span>
                    <span class="legend-pct"> — ${pct}%</span>
                </div>
            </div>`;
    }).join('');
}

// ==================== UTILITIES ====================
function resetButton(btn, orig) { btn.textContent = orig; btn.disabled = false; isSubmitting = false; }

function showCustomAlert(title, message) {
    const backdrop = document.createElement('div');
    backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px;';
    backdrop.innerHTML = `
        <div style="background:white;border-radius:14px;padding:28px;max-width:360px;width:100%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.25);">
            <h3 style="font-size:17px;margin-bottom:8px;color:#1a2744;">${title}</h3>
            <p style="color:#4a5568;font-size:13.5px;margin-bottom:20px;line-height:1.6;">${message}</p>
            <button onclick="this.closest('[style]').remove()" style="padding:10px 28px;background:#1a2744;color:white;border:none;border-radius:7px;font-weight:700;font-size:13px;cursor:pointer;font-family:inherit;">OK</button>
        </div>`;
    backdrop.addEventListener('click', e => { if (e.target === backdrop) backdrop.remove(); });
    document.body.appendChild(backdrop);
    setTimeout(() => backdrop.remove(), 5000);
}

function createConfetti() {
    const colors = ['#1a2744','#046A38','#FF671F','#C6962A','#ffffff'];
    for (let i = 0; i < 45; i++) {
        const el = document.createElement('div');
        el.style.cssText = `
            position:fixed; top:-10px; width:8px; height:8px;
            background:${colors[Math.floor(Math.random()*colors.length)]};
            left:${Math.random()*100}%;
            border-radius:${Math.random()>0.5?'50%':'2px'};
            animation:confettiFall ${2+Math.random()*2}s ease-in forwards;
            z-index:9999;`;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 4000);
    }
}

// Inject confetti keyframe once
const style = document.createElement('style');
style.textContent = `@keyframes confettiFall { to { transform: translateY(100vh) rotate(720deg); opacity:0; } }`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    console.log('🗳️ Voting System Ready');
});
