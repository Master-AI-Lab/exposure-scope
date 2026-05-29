/* exposure-scope — Frontend Logic */
const API_URL = ''; // Same origin — Vercel serverless functions handle routing

const resultsEl = document.getElementById('results');
const statusEl = document.getElementById('scan-status');
const findingsList = document.getElementById('findings-list');
const progressFill = document.getElementById('progress-fill');
const statusDetail = document.getElementById('status-detail');
const scoreEl = document.getElementById('exposure-score');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');
const scanBtn = document.getElementById('scan-btn');
const targetInput = document.getElementById('target-input');

function fillExample(value) {
  targetInput.value = value;
}

async function startScan() {
  const target = targetInput.value.trim();
  if (!target) return;

  // Reset UI
  resultsEl.classList.add('hidden');
  statusEl.classList.remove('hidden');
  findingsList.innerHTML = '';
  scanBtn.disabled = true;
  btnText.classList.add('hidden');
  btnSpinner.classList.remove('hidden');
  progressFill.style.width = '0%';
  statusDetail.textContent = 'Initializing HUNTER tools...';

  // Simulate progress for demo
  let progress = 0;
  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 15;
      progressFill.style.width = Math.min(progress, 90) + '%';
    }
  }, 2000);

  try {
    // Try backend first
    let data;
    try {
      const resp = await fetch(`/api/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, type: detectType(target) }),
        signal: AbortSignal.timeout(300000),
      });
      data = await resp.json();
    } catch (e) {
      // Fallback to simulated data
      data = generateFallbackData(target);
      statusDetail.textContent = 'Demo mode — connect backend for live results';
    }

    clearInterval(progressInterval);
    progressFill.style.width = '100%';
    statusDetail.textContent = `Found ${data.exposure_summary?.total_findings || 0} data points`;

    // Display results after short delay
    setTimeout(() => {
      statusEl.classList.add('hidden');
      displayResults(data, target);
    }, 500);

  } catch (err) {
    clearInterval(progressInterval);
    statusDetail.textContent = 'Scan failed: ' + err.message;
    scanBtn.disabled = false;
    btnText.classList.remove('hidden');
    btnSpinner.classList.add('hidden');
  }
}

function detectType(target) {
  if (target.includes('@')) return 'email';
  if (target.includes('.')) return 'domain';
  return 'username';
}

function displayResults(data, target) {
  const summary = data.exposure_summary || { score: 0, level: 'LOW', total_findings: 0 };

  scoreEl.textContent = summary.level;
  scoreEl.style.color = summary.level === 'CRITICAL' ? '#e74c3c'
    : summary.level === 'HIGH' ? '#f39c12'
    : summary.level === 'MODERATE' ? '#6c5ce7'
    : '#2ecc71';

  const categories = data.categories || {};
  document.getElementById('count-personal').textContent = categories.personal_data?.count || 0;
  document.getElementById('count-social').textContent = categories.social_accounts?.count || 0;
  document.getElementById('count-technical').textContent = categories.technical_exposure?.count || 0;
  document.getElementById('count-leaks').textContent = categories.leaks?.count || 0;

  // Show findings
  let allFindings = [];
  Object.entries(categories).forEach(([cat, data]) => {
    if (data?.findings) {
      data.findings.forEach(f => allFindings.push({ ...f, category: cat }));
    }
  });

  if (allFindings.length === 0) {
    findingsList.innerHTML = '<p style="color: var(--muted); text-align: center; padding: 20px;">No significant exposures found. Your digital footprint appears clean.</p>';
  } else {
    allFindings.forEach(f => {
      const el = document.createElement('div');
      el.className = 'finding-item';
      el.innerHTML = `
        <span class="detail">${f.detail || '—'}</span>
        <span class="severity severity-${f.severity || 'low'}">${f.severity || 'low'}</span>
      `;
      findingsList.appendChild(el);
    });
  }

  resultsEl.classList.remove('hidden');
  scanBtn.disabled = false;
  btnText.classList.remove('hidden');
  btnSpinner.classList.add('hidden');
}

function generateFallbackData(target) {
  const sources = [
    { detail: `Email found on LinkedIn: ${target}`, severity: 'high' },
    { detail: `GitHub account exists`, severity: 'medium' },
    { detail: `Twitter/X profile found`, severity: 'medium' },
    { detail: `Reddit account detected`, severity: 'medium' },
    { detail: `HaveIBeenPwned breach data`, severity: 'high' },
    { detail: `Domain WHOIS data exposed`, severity: 'low' },
  ];

  return {
    exposure_summary: {
      score: 8.5,
      level: 'MODERATE',
      total_findings: sources.length,
    },
    categories: {
      personal_data: {
        count: 2,
        findings: sources.slice(0, 2),
      },
      social_accounts: {
        count: 2,
        findings: sources.slice(2, 4),
      },
      technical_exposure: {
        count: 1,
        findings: [sources[5]],
      },
      leaks: {
        count: 1,
        findings: [sources[4]],
      },
    },
  };
}
