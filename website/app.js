const JOBS = [
  { id: 'j1', title: 'Frontend Developer · React + TS', company: 'TCS', location: 'Nagpur', salary: '₹8–14 LPA', source: 'freehire', skills: ['React', 'TypeScript', 'Tailwind'], relevance: .92, freshH: 2, likes: 124, saves: 42, mutual: 2, hasRef: true, posted: '2h ago', description: 'Build customer-facing products with a team that ships in small, useful steps.' },
  { id: 'j2', title: 'Backend Engineer · Node + Postgres', company: 'Infosys', location: 'Pune', salary: '₹12–18 LPA', source: 'kaggle_india', skills: ['Node.js', 'Postgres', 'Docker'], relevance: .84, freshH: 18, likes: 89, saves: 31, mutual: 0, hasRef: false, posted: '18h ago', description: 'Own reliable APIs and data workflows for teams across India.' },
  { id: 'j3', title: 'Data Scientist · LLM + RAG', company: 'Google', location: 'Bengaluru', salary: '₹22–35 LPA', source: 'freehire', skills: ['Python', 'LLM', 'RAG'], relevance: .88, freshH: 5, likes: 210, saves: 98, mutual: 3, hasRef: true, posted: '5h ago', description: 'Explore useful language systems that move from research to real people.' },
  { id: 'j4', title: 'Product Intern · 0 → 1', company: 'Zerodha', location: 'Mumbai', salary: '₹45k stipend', source: 'kaggle_india', skills: ['Figma', 'SQL', 'Analytics'], relevance: .76, freshH: 36, likes: 67, saves: 22, mutual: 1, hasRef: false, posted: '1d ago', description: 'Learn the craft of product thinking with a team that values clarity.' },
  { id: 'j5', title: 'DevOps Engineer · K8s + CI/CD', company: 'Amazon', location: 'Hyderabad', salary: '₹16–24 LPA', source: 'freehire', skills: ['Kubernetes', 'Docker', 'AWS'], relevance: .81, freshH: 9, likes: 143, saves: 55, mutual: 0, hasRef: true, posted: '9h ago', description: 'Help the next million releases become safer, faster and more boring.' },
  { id: 'j6', title: 'AI Engineer · Multilingual', company: 'Sarvam AI', location: 'Remote · India', salary: '₹18–30 LPA', source: 'freehire', skills: ['ML', 'Hindi NLP', 'Transformers'], relevance: .90, freshH: 1, likes: 301, saves: 112, mutual: 4, hasRef: true, posted: '1h ago', description: 'Build language products that understand the texture of Bharat.' },
  { id: 'j7', title: 'MERN Developer · Nagpur onsite', company: 'Persistent', location: 'Nagpur', salary: '₹10–16 LPA', source: 'kaggle_india', skills: ['React', 'Node.js', 'MongoDB'], relevance: .87, freshH: 3, likes: 98, saves: 34, mutual: 2, hasRef: true, posted: '3h ago', description: 'Join a local team shipping modern web experiences for global users.' },
  { id: 'j8', title: 'Data Analyst · SQL + PowerBI', company: 'Wipro', location: 'Pune', salary: '₹6–9 LPA', source: 'kaggle_india', skills: ['SQL', 'PowerBI', 'Excel'], relevance: .70, freshH: 28, likes: 54, saves: 18, mutual: 0, hasRef: false, posted: '1d ago', description: 'Turn a noisy business question into a clear decision.' },
  { id: 'j9', title: 'Product Designer · Research-led', company: 'Razorpay', location: 'Bengaluru', salary: '₹14–21 LPA', source: 'freehire', skills: ['Figma', 'Research', 'Product'], relevance: .74, freshH: 7, likes: 72, saves: 29, mutual: 1, hasRef: true, posted: '7h ago', description: 'Make complex financial moments feel human and trustworthy.' },
];

const SCHEMES = [
  { id: 's1', name: 'PM Internship Scheme', ministry: 'Ministry of Corporate Affairs', benefit: '12 months + ₹5,000 / month', elig: { age: true, state: true, edu: false }, score: .92, posted: '3h ago', cat: 'Students', note: 'Strong fit for a first work experience.' },
  { id: 's2', name: 'NCS Young Professionals', ministry: 'MSDE · National Career Service', benefit: 'Skill stipend + placement support', elig: { age: true, state: true, edu: true }, score: .78, posted: '1d ago', cat: 'Jobs', note: 'Your profile matches the skill-first pathway.' },
  { id: 's3', name: 'Startup India Seed Fund', ministry: 'DPIIT · Startup India', benefit: 'Up to ₹50L grant for validation', elig: { age: false, state: true, edu: true }, score: .64, posted: '2d ago', cat: 'Startup', note: 'Age proof is the only open question.' },
  { id: 's4', name: 'SWAYAM · NPTEL scholarships', ministry: 'Ministry of Education', benefit: 'Free courses + recognised certificates', elig: { age: true, state: true, edu: true }, score: .88, posted: '6h ago', cat: 'Learning', note: 'A practical bridge into Docker and cloud.' },
  { id: 's5', name: 'PMKVY 4.0', ministry: 'Skill India Digital', benefit: 'Industry-aligned upskilling support', elig: { age: true, state: true, edu: true }, score: .81, posted: '10h ago', cat: 'Learning', note: 'Good option for structured upskilling.' },
  { id: 's6', name: 'Maharashtra Apprenticeship Drive', ministry: 'MSSDS · Maharashtra', benefit: 'Paid apprenticeship + mentor support', elig: { age: true, state: true, edu: false }, score: .86, posted: '14h ago', cat: 'Jobs', note: 'Local and designed for early-career builders.' },
];

const PEERS = [
  { id: 'p1', name: 'Priya Sharma', role: 'SDE @ TCS · Nagpur', skills: ['React', 'Node.js'], dist: 4.2, common: ['React', 'AI/ML'], mutual: 3, int: ['AI/ML', 'Product'], color: '#156b48' },
  { id: 'p2', name: 'Aman Verma', role: 'Data Analyst @ Infosys · Pune', skills: ['Python', 'SQL'], dist: 12.8, common: ['Python'], mutual: 1, int: ['Data'], color: '#5076a8' },
  { id: 'p3', name: 'Rohit Gupta', role: 'Founder @ BharatBuild', skills: ['Product', 'Growth'], dist: 2.1, common: ['Product'], mutual: 5, int: ['Startup'], color: '#b86e78' },
  { id: 'p4', name: 'Sneha Das', role: 'ML Intern @ Sarvam · Remote', skills: ['Transformers', 'Hindi NLP'], dist: 7.4, common: ['AI/ML'], mutual: 2, int: ['AI/ML'], color: '#a278b8' },
  { id: 'p5', name: 'Arjun Mehta', role: 'DevOps @ Amazon · Hyderabad', skills: ['K8s', 'Docker'], dist: 18.3, common: ['Docker'], mutual: 0, int: ['Cloud'], color: '#9b710d' },
  { id: 'p6', name: 'Kavya Iyer', role: 'Design @ Zerodha · Mumbai', skills: ['Figma', 'Research'], dist: 9.1, common: ['Design'], mutual: 2, int: ['Design'], color: '#d46d3b' },
];

let STARTUPS = [
  { id: 'st1', title: 'Bharat Tutor · AI for Tier-3', owner: 'You', cat: 'EdTech', need: ['React', 'LLM', 'Hindi'], match: .91, likes: 42, desc: 'Voice-first tutor for Hindi and Marathi that works on low bandwidth. Need one LLM builder and a calm frontend thinker.' },
  { id: 'st2', title: 'Kisan Mandi Connect', owner: 'Rohit G.', cat: 'AgriTech', need: ['Node', 'Maps', 'UPI'], match: .76, likes: 28, desc: 'Farmers to buyers with real mandi prices, lightweight logistics and a UPI-first checkout.' },
  { id: 'st3', title: 'Health Saathi · ASHA helper', owner: 'Sneha D.', cat: 'Health', need: ['ML', 'React Native'], match: .82, likes: 35, desc: 'An offline-friendly assistant for ASHA workers: schedule, transcribe, translate and keep moving.' },
  { id: 'st4', title: 'Namma Skill Circles', owner: 'Kavya I.', cat: 'Community', need: ['Product', 'Research', 'React'], match: .86, likes: 19, desc: 'Small, local skill circles that make it easier to learn in public and find collaborators nearby.' },
];

const POOL = ['React', 'Python', 'Node.js', 'SQL', 'Docker', 'Kubernetes', 'LLM', 'RAG', 'TypeScript', 'Figma', 'AWS', 'Product', 'AI/ML', 'Data', 'Startup', 'Design', 'Cloud', 'Hindi NLP'];
const NAV_PRIMARY = [
  ['landing', 'Overview', 'home'], ['feed', 'For you', 'spark', '3'], ['resume', 'Resume twin', 'file'], ['peers', 'Nearby tribe', 'users'], ['schemes', 'Govt schemes', 'landmark'], ['startups', 'Startup bazaar', 'rocket'],
];
const NAV_SECONDARY = [['recent', 'Recent pulse', 'clock'], ['profile', 'Profile DNA', 'user'], ['admin', 'Simulation lab', 'sliders']];
const ROUTE_LABELS = { landing: 'Overview', feed: 'For you', resume: 'Resume twin', peers: 'Nearby tribe', schemes: 'Govt schemes', startups: 'Startup bazaar', recent: 'Recent pulse', profile: 'Profile DNA', admin: 'Simulation lab' };
// Local development (localhost / 127.0.0.1 / opened as a file) talks to the
// local backend; hosted deployments call the Hugging Face Space instead.
const PROD_API_BASE = 'https://sunsau91-bharat-career-twin.hf.space/api';
const isLocalRun = !location.hostname || ['localhost', '127.0.0.1'].includes(location.hostname);
const API_BASE = (window.BCT_API_BASE || (isLocalRun ? 'http://127.0.0.1:8000/api' : PROD_API_BASE)).replace(/\/$/, '');
const DEMO_USER = window.BCT_DEMO_USER || 'demo_fresher';

const state = {
  interests: ['React', 'AI/ML', 'Product'],
  hates: ['Night shift', 'Sales'],
  skills: ['React', 'JavaScript', 'Python', 'TypeScript'],
  ats: 82,
  weights: { relevance: .35, skill: .20, social: .15, freshness: .12, popularity: .08, hate: .4 },
  tab: 'all',
  limit: 6,
  lang: 'EN',
  focus: 'career',
  steer: 'more coding roles, less night shift',
  diversity: 72,
  activeRoute: 'landing',
  memory: ['Prefer product-minded teams', 'Nagpur / open to remote', 'React is a core strength', 'Turn down night shifts', 'Show free learning paths', 'Keep referrals visible'],
  memoryLog: [
    { text: 'Added “prefer product-minded teams”', time: 'Today · 09:20', tone: '' },
    { text: 'Saved 3 React + AI roles', time: 'Yesterday · 18:40', tone: 'green' },
    { text: 'Turned down night shift roles', time: 'Tue · 11:12', tone: '' },
  ],
  shareTitle: 'Bharat Career Twin signal',
  shareUrl: 'https://bharatcareertwin.local/signal',
  referralLanguage: 'hinglish',
  referralPath: null,
  referralDrafts: null,
  selectedSearch: 0,
  renderToken: 0,
  api: { status: 'idle', feedKey: '', feedItems: null, trace: [], backends: null },
};

const ICON_PATHS = {
  home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1Z"/>',
  spark: '<path d="m12 2 1.45 5.55L19 9l-5.55 1.45L12 16l-1.45-5.55L5 9l5.55-1.45Z"/><path d="m19 15 .62 2.38L22 18l-2.38.62L19 21l-.62-2.38L16 18l2.38-.62Z"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  landmark: '<path d="M3 10h18M5 10v9M9 10v9M15 10v9M19 10v9M3 21h18M4 7l8-4 8 4Z"/>',
  rocket: '<path d="M14.5 6.5 17 4a5 5 0 0 1 3 3l-2.5 2.5M6.5 14.5 4 17a5 5 0 0 0 3 3l2.5-2.5M8 16l-4 1 1-4 5-5a6 6 0 0 1 8 8l-5 5-4 1 1-4Z"/><circle cx="15" cy="9" r="1"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  user: '<circle cx="12" cy="7" r="4"/><path d="M4 22a8 8 0 0 1 16 0"/>',
  sliders: '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="10" cy="18" r="2"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  chevron: '<path d="m14 6-6 6 6 6"/>',
  upload: '<path d="M12 16V4M8 8l4-4 4 4M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L8 18l-4 1 1-4Z"/>',
  copy: '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  route: '<circle cx="5" cy="6" r="2"/><circle cx="19" cy="18" r="2"/><path d="M7 6h5a4 4 0 0 1 4 4v4a4 4 0 0 0 4 4M5 8v4a4 4 0 0 0 4 4h6"/>',
  network: '<circle cx="12" cy="12" r="2"/><circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="m10.5 10.5-4-4M13.5 10.5l4-4M10.5 13.5l-4 4M13.5 13.5l4 4"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  play: '<path d="m8 5 11 7-11 7Z"/>',
  heart: '<path d="M20.8 8.8c0 5.5-8.8 10-8.8 10s-8.8-4.5-8.8-10A4.8 4.8 0 0 1 12 6a4.8 4.8 0 0 1 8.8 2.8Z"/>',
  bookmark: '<path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1Z"/>',
  eyeoff: '<path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 4.2A10.8 10.8 0 0 1 12 4c5 0 8.3 4 9.5 6a12.8 12.8 0 0 1-3.1 3.6M6.2 6.2C4.6 7.3 3.4 9 2.5 10c1.2 2 4.5 6 9.5 6 1 0 1.9-.2 2.7-.5"/>',
  share: '<circle cx="18" cy="5" r="2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="19" r="2"/><path d="m8 11 8-5M8 13l8 5"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
};

function icon(name) {
  return `<svg viewBox="0 0 24 24" aria-hidden="true">${ICON_PATHS[name] || ICON_PATHS.spark}</svg>`;
}

function esc(value = '') {
  return String(value).replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}

function toast(message, tone = 'default') {
  const stack = document.getElementById('toastStack');
  if (!stack) return;
  const item = document.createElement('div');
  item.className = `toast ${tone === 'success' ? 'success' : ''}`;
  item.innerHTML = `<i></i><span>${esc(message)}</span>`;
  stack.appendChild(item);
  window.setTimeout(() => {
    item.classList.add('out');
    window.setTimeout(() => item.remove(), 260);
  }, 2600);
}

async function apiRequest(path, options = {}) {
  const headers = { 'X-Demo-User': DEMO_USER, ...(options.headers || {}) };
  const isForm = options.body instanceof FormData;
  if (!isForm && options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    let detail = `API request failed (${response.status})`;
    try { const body = await response.json(); detail = body.detail?.message || body.detail || detail; } catch (error) { /* fallback detail is enough for local mode */ }
    throw new Error(detail);
  }
  return response.json();
}

function renderAgentTrace(trace = []) {
  const target = document.getElementById('agentTrace');
  if (!target) return;
  const names = trace.length ? trace.map(step => step.agent) : ['profiler', 'interest miner', 'matcher', 'social connector', 'coach gap', 'feed ranker'];
  target.innerHTML = `<span class="agent-trace-label">${state.api.status === 'ready' ? 'agent trace' : 'local trace'}</span>${names.map(name => `<span class="agent-trace-step"><i></i>${esc(String(name).replace(/_/g, ' '))}</span>`).join('')}`;
}

function normalizeApiItem(item) {
  if (item.type === 'job') {
    const breakdown = item.breakdown || {};
    return {
      ...item,
      location: item.location || 'Remote',
      posted: item.posted_ago || 'today',
      freshH: item.fresh_hours || 12,
      likes: item.likes || 0,
      saves: item.saves || 0,
      mutual: item.mutual_count || 0,
      hasRef: Boolean(item.has_referral),
      relevance: breakdown.relevance || item.match_score || .72,
      detail: {
        final: item.match_score || .72,
        relevance: breakdown.relevance || item.match_score || .72,
        skillOverlap: breakdown.skill_overlap || 0,
        social: breakdown.social || 0,
        freshness: breakdown.freshness || 0,
        hate: breakdown.hate || 0,
      },
    };
  }
  if (item.type === 'scheme') {
    const eligibility = item.eligibility || {};
    return { ...item, name: item.name, cat: item.category || 'Scheme', score: (item.eligibility_score || 0) / 100, elig: { ...eligibility, edu: eligibility.edu ?? eligibility.education }, posted: item.posted_ago || 'today', note: 'Eligibility mapped from your profile.' };
  }
  if (item.type === 'peer') {
    return { ...item, dist: item.distance_km, common: item.skills?.slice(0, 2) || [], mutual: item.mutual_count || 0, int: item.interests || [], color: item.color || '#5076a8' };
  }
  if (item.type === 'startup') {
    return { ...item, desc: item.description, cat: item.category || 'Community', need: item.skills || [], match: item.match_score || .72, likes: item.likes || 0 };
  }
  return item;
}

function renderCurrentFeedCards() {
  const list = document.getElementById('feedList');
  if (!list) return;
  if (state.api.status === 'ready' && Array.isArray(state.api.feedItems)) {
    list.innerHTML = state.api.feedItems.map((item, index) => item.type === 'job' ? cardJob(item, index) : item.type === 'scheme' ? cardScheme(item, index) : item.type === 'peer' ? cardPeer(item, index) : cardStartup(item, index)).join('') || '<div class="search-empty">No signals match this steer yet.</div>';
    return;
  }
  list.innerHTML = feedItems().join('') || '<div class="search-empty">No signals match this steer yet.</div>';
}

async function fetchApiFeed(key, token) {
  state.api.status = 'loading';
  try {
    const params = new URLSearchParams({ offset: '0', limit: String(Math.max(state.limit, 12)), type: state.tab === 'all' || state.tab === 'recent' ? 'all' : state.tab, steer: state.steer });
    const data = await apiRequest(`/feed?${params.toString()}`);
    if (key !== state.api.feedKey || token !== state.renderToken) return;
    const items = (data.items || []).map(normalizeApiItem);
    state.api.feedItems = state.tab === 'recent' ? items.filter(item => item.type === 'job' && Number(item.fresh_hours || 999) < 24) : items;
    state.api.trace = data.agent_trace || [];
    state.api.backends = data.backends || {};
    state.api.status = 'ready';
    sendImpressions(state.api.feedItems, state.api.backends);
    renderAgentTrace(state.api.trace);
    renderCurrentFeedCards();
  } catch (error) {
    if (key !== state.api.feedKey || token !== state.renderToken) return;
    state.api.status = 'fallback';
    state.api.feedItems = null;
    renderAgentTrace();
    renderCurrentFeedCards();
  }
}

function sendInteraction(action, itemId, itemType = 'job', reason = null) {
  apiRequest('/interactions', { method: 'POST', body: JSON.stringify({ item_id: itemId, item_type: itemType, action, reason, dwell_ms: 0 }) }).catch(() => {});
}

function sendImpressions(items, backends = {}) {
  if (!Array.isArray(items) || !items.length) return;
  const impressions = items.map((item, index) => ({
    item_id: item.id,
    item_type: item.type || 'job',
    rank_position: index + 1,
    candidate_source: backends.candidate_backend || 'feed',
    model_version: backends.model_version || 'rules-v1',
    surface: state.activeRoute || 'feed',
    context: { tab: state.tab, steer: state.steer || '' },
  }));
  apiRequest('/impressions', { method: 'POST', body: JSON.stringify({ impressions }) }).catch(() => {});
}

async function loadModelStatus() {
  try {
    const [model, stats] = await Promise.all([apiRequest('/model/status'), apiRequest('/stats')]);
    const backend = document.getElementById('modelBackend');
    const version = document.getElementById('modelVersion');
    const ndcg = document.getElementById('modelNdcg');
    const recall = document.getElementById('modelRecall');
    const impressions = document.getElementById('modelImpressions');
    if (backend) backend.textContent = model.available ? 'learned ranker' : 'rules fallback';
    if (version) version.textContent = model.available ? `${model.model_version} · ${model.trained_examples || 0} examples` : 'train a model artifact to enable learning';
    if (ndcg) ndcg.textContent = model.metrics?.ndcg_at_10 != null ? Number(model.metrics.ndcg_at_10).toFixed(2) : '—';
    if (recall) recall.textContent = model.metrics?.recall_at_10 != null ? `Recall@10 ${Number(model.metrics.recall_at_10).toFixed(2)}` : 'temporal validation';
    if (impressions) impressions.textContent = String(stats.impressions || 0);
  } catch (error) {
    // Static admin values remain useful when the API is offline.
  }
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add('visible');
  modal.setAttribute('aria-hidden', 'false');
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove('visible');
  modal.setAttribute('aria-hidden', 'true');
}

function closeAllModals() {
  ['searchModal', 'shareSheet', 'explainSheet', 'referralModal', 'simulationModal'].forEach(closeModal);
}

function buildNav() {
  const render = items => items.map(([route, label, iconName, badge]) => `<button class="nav-item ${route === state.activeRoute ? 'active' : ''}" data-route="${route}" title="${label}"><span class="nav-icon icon">${icon(iconName)}</span><span class="nav-text">${label}</span>${badge ? `<span class="nav-badge">${badge}</span>` : ''}</button>`).join('');
  document.getElementById('primaryNav').innerHTML = render(NAV_PRIMARY);
  document.getElementById('secondaryNav').innerHTML = render(NAV_SECONDARY);
}

function updateBreadcrumb(route) {
  document.getElementById('breadcrumb').innerHTML = `<span>AgentFeed</span><span class="breadcrumb-slash">/</span><strong>${ROUTE_LABELS[route] || 'Overview'}</strong>`;
}

function go(route) {
  if (!ROUTE_LABELS[route]) return;
  state.activeRoute = route;
  document.querySelectorAll('[data-page]').forEach(page => page.classList.toggle('active', page.dataset.page === route));
  buildNav();
  updateBreadcrumb(route);
  document.querySelector('.page-wrap')?.scrollTo?.({ top: 0, behavior: 'smooth' });
  window.scrollTo({ top: 0, behavior: 'smooth' });
  closeAllModals();
  document.getElementById('sidebar')?.classList.remove('mobile-open');
  document.getElementById('mobileBackdrop')?.classList.remove('visible');
  if (route === 'feed') renderFeed();
  if (route === 'peers') renderPeers();
  if (route === 'schemes') renderSchemes();
  if (route === 'startups') renderStartups();
  if (route === 'recent') renderRecent();
  if (route === 'profile') renderProfile();
}

function openSearch() {
  openModal('searchModal');
  const input = document.getElementById('searchInput');
  input.value = '';
  state.selectedSearch = 0;
  renderSearch('');
  window.setTimeout(() => input.focus(), 20);
}

function sourceTag(job) {
  return job.source === 'freehire' ? '<span class="source-tag">● freehire · live</span>' : '<span class="source-tag archive">archive signal</span>';
}

function scoreColor(score) {
  if (score >= .85) return { color: 'var(--green)', track: '#e4f1e5' };
  if (score >= .65) return { color: 'var(--saffron)', track: '#f8e5db' };
  return { color: 'var(--muted)', track: '#edf0ec' };
}

function matchCircle(score) {
  const pct = Math.round(score * 100);
  const colors = scoreColor(score);
  return `<div class="match-circle" style="--match:${pct}%;--circle-color:${colors.color};--circle-track:${colors.track}"><strong>${pct}%</strong><span>match</span></div>`;
}

function avatarStack(count = 0) {
  const letters = ['P', 'A', 'S', 'K'];
  const colors = ['#156b48', '#f26b3a', '#5076a8', '#b86e78'];
  const visible = Math.min(3, count);
  if (!visible) return '<div class="mutual-row"><span>Be the first warm signal.</span></div>';
  const avatars = Array.from({ length: visible }, (_, index) => `<i style="background:${colors[index]}">${letters[index]}</i>`).join('');
  return `<div class="mutual-row"><span class="avatar-stack">${avatars}</span><span>${count} mutual${count === 1 ? '' : 's'} liked this</span></div>`;
}

function hybrid(item) {
  const w = state.weights;
  const skillPool = [...state.skills, ...state.interests];
  const skillOverlap = item.skills?.length ? Math.min(1, item.skills.filter(skill => skillPool.some(saved => saved.toLowerCase() === skill.toLowerCase())).length / Math.max(1, item.skills.length)) : .5;
  const social = Math.min(1, ((item.mutual || 0) / 5) * .55 + (item.hasRef ? .45 : 0));
  const freshness = Math.exp(-(item.freshH || 12) / 72);
  const popularity = Math.min(1, Math.log(1 + (item.likes || 0) + (item.saves || 0) * 2) / Math.log(120));
  const hateText = `${item.title || ''} ${(item.skills || []).join(' ')}`.toLowerCase();
  const hatePenalty = state.hates.some(hate => hateText.includes(hate.toLowerCase())) ? .72 : .08;
  const steer = state.steer.toLowerCase();
  const steerLocal = /nagpur|near me|local|maharashtra/.test(steer) && /nagpur|maharashtra/.test((item.location || '').toLowerCase()) ? .08 : 0;
  const steerStudy = /study|scheme|course|learning/.test(steer) && item.type === 'scheme' ? .1 : 0;
  const steerStartup = /startup|founder|idea/.test(steer) && item.type === 'startup' ? .1 : 0;
  const focusBoost = state.focus === 'study' && item.type === 'scheme' ? .09 : state.focus === 'relax' && item.type === 'peer' ? .06 : 0;
  const final = w.relevance * (item.relevance || item.score || .72) + w.skill * skillOverlap + w.social * social + w.freshness * freshness + w.popularity * popularity - w.hate * hatePenalty + steerLocal + steerStudy + steerStartup + focusBoost + (item.hasRef ? .035 : 0);
  return { final: Math.max(0, Math.min(1, final)), skillOverlap, social, freshness, hatePenalty, popularity, relevance: item.relevance || item.score || .72 };
}

function mmr(candidates, limit = 10, lambda = .72) {
  const similarity = (a, b) => {
    const aa = new Set(a.skills || []); const bb = new Set(b.skills || []);
    const intersection = [...aa].filter(item => bb.has(item)).length;
    const union = new Set([...aa, ...bb]).size;
    return union ? intersection / union : 0;
  };
  const pool = [...candidates].sort((a, b) => b.detail.final - a.detail.final);
  if (!pool.length) return [];
  const selected = [pool.shift()];
  while (selected.length < limit && pool.length) {
    let bestIndex = 0; let bestValue = -Infinity;
    pool.forEach((candidate, index) => {
      const maxSimilarity = Math.max(...selected.map(item => similarity(candidate, item)));
      const value = lambda * candidate.detail.final - (1 - lambda) * maxSimilarity;
      if (value > bestValue) { bestValue = value; bestIndex = index; }
    });
    selected.push(pool.splice(bestIndex, 1)[0]);
  }
  return selected;
}

function renderStories() {
  const stories = [
    { label: 'TCS · React', time: '2h ago', color: 'linear-gradient(135deg,#f26b3a,#f4c54b)', letter: 'T' },
    { label: 'Sarvam AI', time: '1h ago', color: 'linear-gradient(135deg,#156b48,#9bc8a4)', letter: 'S' },
    { label: 'PM Internship', time: '3h ago', color: 'linear-gradient(135deg,#5076a8,#a5c8ec)', letter: '₹' },
    { label: 'Nagpur tribe', time: '5h ago', color: 'linear-gradient(135deg,#b86e78,#e2a8a9)', letter: 'N' },
    { label: 'Docker gap', time: 'today', color: 'linear-gradient(135deg,#d6a837,#f4dc98)', letter: '↗' },
  ];
  document.getElementById('stories').innerHTML = stories.map(story => `<button class="story"><span class="new-label">new</span><span class="story-ring" style="background:${story.color}"><span>${story.letter}</span></span><strong>${story.label}</strong><small>${story.time} · signal</small></button>`).join('');
}

function renderTabs() {
  const tabs = [['all', 'For you'], ['job', 'Jobs'], ['scheme', 'Schemes'], ['peer', 'Peers'], ['startup', 'Startups'], ['recent', 'Recent']];
  document.getElementById('tabs').innerHTML = tabs.map(([key, label]) => `<button class="tab ${state.tab === key ? 'active' : ''}" data-tab="${key}">${label}</button>`).join('');
}

function renderChips() {
  const interests = document.getElementById('interestChips');
  const hates = document.getElementById('hateChips');
  if (!interests || !hates) return;
  interests.innerHTML = POOL.slice(0, 12).map(value => `<button class="chip ${state.interests.includes(value) ? 'active' : ''}" data-dna-interest="${esc(value)}">${esc(value)}</button>`).join('');
  hates.innerHTML = ['Sales', 'Night shift', 'BPO', 'Long commute'].map(value => `<button class="chip hate ${state.hates.includes(value) ? 'active' : ''}" data-dna-hate="${esc(value)}">${esc(value)}</button>`).join('');
  const gauge = document.getElementById('atsGauge');
  if (gauge) gauge.style.background = `conic-gradient(var(--saffron) ${state.ats}%, #f2e6d9 0)`;
  const score = document.getElementById('atsScore');
  if (score) score.textContent = `${state.ats}%`;
  const bigGauge = document.getElementById('bigGauge');
  if (bigGauge) bigGauge.style.background = `conic-gradient(var(--saffron) ${state.ats}%, #f4e1d6 0)`;
  const bigScore = document.getElementById('bigScore');
  if (bigScore) bigScore.textContent = state.ats;
  const highlights = document.getElementById('resumeHighlights');
  if (highlights) highlights.innerHTML = ['React product delivery', 'Strong JavaScript base', 'Clear communication'].map(item => `<span><i></i>${item}</span>`).join('');
}

function renderDigest() {
  const target = document.getElementById('digestList');
  if (!target) return;
  target.innerHTML = [
    ['orange', '3 new 90% roles near Nagpur', '2h · fresh from freehire'],
    ['green', 'PM Internship is a 92% eligibility fit', '3h · India scheme'],
    ['blue', 'Priya can open a warm path to TCS', 'today · 2 hops away'],
  ].map(([tone, text, time]) => `<div class="digest-item ${tone}"><i></i><div><p>${text}</p><small>${time}</small></div></div>`).join('');
}

function renderDiversity() {
  const score = Math.max(40, Math.min(94, state.diversity + (state.focus === 'relax' ? 7 : 0) - (state.tab === 'job' ? 8 : 0)));
  const fill = document.getElementById('diversityFill'); const marker = document.getElementById('diversityMarker'); const scoreEl = document.getElementById('diversityScore'); const badge = document.getElementById('healthBadge');
  if (!fill || !marker || !scoreEl || !badge) return;
  fill.style.width = `${score}%`; marker.style.left = `${score}%`; scoreEl.textContent = score;
  badge.textContent = score >= 68 ? 'Balanced' : 'Narrowing';
  badge.style.color = score >= 68 ? 'var(--green)' : 'var(--saffron-dark)';
  badge.style.background = score >= 68 ? 'var(--green-soft)' : 'var(--saffron-soft)';
  const copy = document.getElementById('diversityCopy');
  if (copy) copy.textContent = score >= 68 ? 'Your feed blends roles, schemes and people without losing your edge.' : 'This view is getting narrow. Try a wider focus to keep new paths visible.';
}

function cardJob(job, index = 0) {
  const detail = job.detail || hybrid(job);
  const topSkills = job.skills.map(skill => `<span class="feed-tag ${state.skills.includes(skill) ? 'match' : ''}">${esc(skill)}</span>`).join('');
  const reason = job.hasRef ? `Matched <strong>${Math.round(detail.relevance * 100)}% relevance</strong> + a warm path through your graph.` : `Matched <strong>${Math.round(detail.skillOverlap * 100)}% skill overlap</strong> and fresh signals from today.`;
  return `<article class="feed-card job-card card-enter-${Math.min(5, index + 1)}" data-card-id="${job.id}"><div class="feed-card-top"><div class="feed-card-main">${matchCircle(detail.final)}<div><div class="feed-card-title"><h3>${esc(job.title)}</h3>${sourceTag(job)}</div><div class="feed-meta">${esc(job.company)} · ${esc(job.location)} · ${esc(job.salary)} · ${esc(job.posted)}</div><div class="feed-tags">${topSkills}</div></div></div><div class="feed-card-side"><button class="card-icon-button" data-card-action="save" data-id="${job.id}" aria-label="Save ${esc(job.title)}"><span class="icon">${icon('bookmark')}</span></button><button class="card-icon-button" data-card-action="share" data-id="${job.id}" data-title="${esc(job.title)}" aria-label="Share ${esc(job.title)}"><span class="icon">${icon('share')}</span></button></div></div><div class="reason-strip"><span class="icon">${icon('spark')}</span><span>${reason}</span></div>${avatarStack(job.mutual)}<div class="feed-card-actions"><button class="card-action primary" data-card-action="apply" data-id="${job.id}">Apply <span>↗</span></button><button class="card-action" data-card-action="referral" data-id="${job.id}"><span class="icon">${icon('route')}</span>Referral</button><button class="card-action" data-card-action="why" data-id="${job.id}">Why?</button><button class="card-action" data-card-action="like" data-id="${job.id}"><span class="icon">${icon('heart')}</span>Like</button><button class="card-action" data-card-action="hide" data-id="${job.id}"><span class="icon">${icon('eyeoff')}</span>Hide</button><span class="breakdown"><b>${Math.round(detail.final * 100)}%</b> final signal · ${Math.round(detail.freshness * 100)}% fresh</span></div></article>`;
}

function cardScheme(scheme, index = 0) {
  const eligible = scheme.score >= .75;
  const chips = [['Age', scheme.elig.age], ['State', scheme.elig.state], ['Education', scheme.elig.edu]].map(([label, ok]) => `<span class="eligibility-chip ${ok ? 'yes' : 'no'}">${label} ${ok ? '✓' : '—'}</span>`).join('');
  return `<article class="feed-card scheme-card card-enter-${Math.min(5, index + 1)}" data-card-id="${scheme.id}"><div class="feed-card-top"><div class="feed-card-main"><div class="scheme-symbol">₹</div><div><div class="feed-card-title"><h3>${esc(scheme.name)}</h3><span class="source-tag">india · ${esc(scheme.cat)}</span></div><div class="feed-meta">${esc(scheme.ministry)} · ${esc(scheme.posted)}</div></div></div><div class="feed-card-side"><button class="card-icon-button" data-card-action="share" data-id="${scheme.id}" data-title="${esc(scheme.name)}" aria-label="Share scheme"><span class="icon">${icon('share')}</span></button></div></div><div class="reason-strip"><span class="icon">${icon('check')}</span><span><strong>${Math.round(scheme.score * 100)}% eligible</strong> · ${esc(scheme.note)}</span></div><div class="eligibility-row">${chips}</div><div class="feed-card-actions"><button class="card-action primary" data-card-action="open-scheme" data-id="${scheme.id}">See eligibility <span>↗</span></button><button class="card-action" data-card-action="share" data-id="${scheme.id}" data-title="${esc(scheme.name)}">Share QR</button><span class="breakdown"><b>${eligible ? 'good fit' : 'check proof'}</b> · freshness ${esc(scheme.posted)}</span></div></article>`;
}

function cardPeer(peer, index = 0) {
  return `<article class="feed-card peer-card card-enter-${Math.min(5, index + 1)}" data-card-id="${peer.id}"><div class="feed-card-top"><div class="peer-person"><div class="peer-avatar" style="background:${peer.color}">${esc(peer.name.charAt(0))}</div><div><div class="feed-card-title"><h3>${esc(peer.name)}</h3><span class="source-tag">${peer.dist} km</span></div><div class="peer-role">${esc(peer.role)}</div></div></div><button class="card-icon-button" data-card-action="share" data-id="${peer.id}" data-title="${esc(peer.name)}"><span class="icon">${icon('share')}</span></button></div><div class="peer-extra"><span class="feed-tag match">${peer.mutual} mutuals</span>${peer.common.map(skill => `<span class="feed-tag">${esc(skill)} in common</span>`).join('')}</div><div class="reason-strip"><span class="icon">${icon('users')}</span><span>Your graph overlaps on <strong>${esc(peer.common.join(', '))}</strong>. Start with one specific question.</span></div><div class="feed-card-actions"><button class="card-action primary" data-card-action="connect" data-id="${peer.id}">Connect <span>↗</span></button><button class="card-action" data-card-action="referral" data-id="${peer.id}">Find path</button><button class="card-action" data-card-action="share" data-id="${peer.id}" data-title="${esc(peer.name)}">Share</button></div></article>`;
}

function cardStartup(startup, index = 0) {
  return `<article class="feed-card startup-card card-enter-${Math.min(5, index + 1)}" data-card-id="${startup.id}"><div class="feed-card-top"><div class="feed-card-main"><div class="startup-icon">✦</div><div><div class="feed-card-title"><h3>${esc(startup.title)}</h3><span class="source-tag archive">${esc(startup.cat)}</span></div><div class="startup-owner">by ${esc(startup.owner)} · ${startup.likes} likes</div></div></div><button class="card-icon-button" data-card-action="share" data-id="${startup.id}" data-title="${esc(startup.title)}"><span class="icon">${icon('share')}</span></button></div><p class="feed-meta">${esc(startup.desc)}</p><div class="startup-extra">${startup.need.map(skill => `<span class="feed-tag match">${esc(skill)}</span>`).join('')}</div><div class="reason-strip"><span class="icon">${icon('spark')}</span><span><strong>${Math.round(startup.match * 100)}% fit</strong> · your skills can make this idea more real.</span></div><div class="feed-card-actions"><button class="card-action primary" data-card-action="help" data-id="${startup.id}">I can help <span>↗</span></button><button class="card-action" data-card-action="share" data-id="${startup.id}" data-title="${esc(startup.title)}">Share QR</button></div></article>`;
}

function feedItems() {
  if (state.tab === 'job') return mmr(JOBS.map(job => ({ ...job, detail: hybrid(job) })), state.limit).map((job, index) => cardJob(job, index));
  if (state.tab === 'scheme') return SCHEMES.filter(scheme => !document.getElementById('eligibleOnly')?.checked || scheme.score >= .75).map((scheme, index) => cardScheme(scheme, index));
  if (state.tab === 'peer') return PEERS.map((peer, index) => cardPeer(peer, index));
  if (state.tab === 'startup') return STARTUPS.map((startup, index) => cardStartup(startup, index));
  if (state.tab === 'recent') return JOBS.filter(job => job.freshH < 24).map(job => ({ ...job, detail: hybrid(job) })).map((job, index) => cardJob(job, index));
  const rankedJobs = mmr(JOBS.map(job => ({ ...job, detail: hybrid(job) })), state.limit);
  const mixed = [];
  rankedJobs.slice(0, 3).forEach((job, index) => mixed.push(cardJob(job, index)));
  mixed.push(cardScheme(SCHEMES[0], 3));
  mixed.push(cardPeer(PEERS[0], 4));
  mixed.push(cardStartup(STARTUPS[0], 5));
  rankedJobs.slice(3, state.limit).forEach((job, index) => mixed.push(cardJob(job, index + 6)));
  return mixed;
}

function renderFeed() {
  const list = document.getElementById('feedList');
  if (!list) return;
  renderTabs(); renderStories(); renderChips(); renderDigest(); renderDiversity();
  const token = ++state.renderToken;
  const key = `${state.tab}|${state.limit}|${state.steer}`;
  state.api.feedKey = key;
  state.api.status = 'loading';
  state.api.feedItems = null;
  list.innerHTML = '<div class="skeleton-card"></div><div class="skeleton-card"></div>';
  renderAgentTrace();
  fetchApiFeed(key, token);
  window.setTimeout(() => {
    if (token !== state.renderToken) return;
    if (state.api.status === 'loading') {
      state.api.status = 'fallback';
      state.api.feedItems = null;
      renderAgentTrace();
    }
    renderCurrentFeedCards();
  }, 4000);
}

function renderPeers() {
  const grid = document.getElementById('peerGrid'); if (!grid) return;
  const skill = document.getElementById('peerSkill').value.trim().toLowerCase();
  const radius = Number(document.getElementById('peerRadius').value);
  const list = PEERS.filter(peer => peer.dist <= radius && (!skill || `${peer.skills.join(' ')} ${peer.int.join(' ')} ${peer.role}`.toLowerCase().includes(skill)));
  grid.innerHTML = list.length ? list.map((peer, index) => cardPeer(peer, index)).join('') : `<div class="search-empty">No one in ${radius} km matches “${esc(skill)}”.</div>`;
  const graph = document.getElementById('graphView');
  if (graph.classList.contains('visible')) drawGraph();
}

function renderSchemes() {
  const grid = document.getElementById('schemeGrid'); if (!grid) return;
  const only = document.getElementById('eligibleOnly')?.checked;
  const list = SCHEMES.filter(scheme => !only || scheme.score >= .75);
  grid.innerHTML = list.map((scheme, index) => `<article class="scheme-card" style="animation:cardIn .45s ${index * 45}ms both"><div class="scheme-card-top"><div class="scheme-symbol">₹</div><span class="scheme-score">${Math.round(scheme.score * 100)}% fit</span></div><h3>${esc(scheme.name)}</h3><div class="scheme-ministry">${esc(scheme.ministry)} · ${esc(scheme.posted)}</div><p class="scheme-benefit">${esc(scheme.benefit)}</p><div class="eligibility-row"><span class="eligibility-chip ${scheme.elig.age ? 'yes' : 'no'}">Age ${scheme.elig.age ? '✓' : '—'}</span><span class="eligibility-chip ${scheme.elig.state ? 'yes' : 'no'}">State ${scheme.elig.state ? '✓' : '—'}</span><span class="eligibility-chip ${scheme.elig.edu ? 'yes' : 'no'}">Education ${scheme.elig.edu ? '✓' : '—'}</span></div><div class="feed-card-actions"><button class="card-action primary" data-card-action="open-scheme" data-id="${scheme.id}">See eligibility <span>↗</span></button><button class="card-action" data-card-action="share" data-id="${scheme.id}" data-title="${esc(scheme.name)}">Share</button></div></article>`).join('');
}

function renderStartups() {
  const list = document.getElementById('startupList'); if (!list) return;
  list.innerHTML = STARTUPS.map((startup, index) => `<article class="startup-card" style="animation:cardIn .45s ${index * 55}ms both"><div class="feed-card-top"><div class="startup-icon">✦</div><span class="source-tag archive">${esc(startup.cat)}</span></div><h3>${esc(startup.title)}</h3><p>${esc(startup.desc)}</p><div class="startup-tags">${startup.need.map(skill => `<span class="startup-tag">${esc(skill)}</span>`).join('')}</div><div class="startup-score"><b>${Math.round(startup.match * 100)}% fit</b><span>· ${startup.likes} likes · by ${esc(startup.owner)}</span></div><div class="feed-card-actions"><button class="card-action primary" data-card-action="help" data-id="${startup.id}">I can help <span>↗</span></button><button class="card-action" data-card-action="share" data-id="${startup.id}" data-title="${esc(startup.title)}">Share QR</button></div></article>`).join('');
}

function renderRecent() {
  const list = document.getElementById('recentList'); if (!list) return;
  const jobs = JOBS.filter(job => job.freshH < 24);
  list.innerHTML = jobs.map((job, index) => `<div class="recent-item"><div class="recent-time">${esc(job.posted)}<br /><span>${index < 2 ? 'new' : 'today'}</span></div><div class="recent-content">${cardJob({ ...job, detail: hybrid(job) }, index)}</div></div>`).join('');
}

function renderProfile() {
  const grid = document.getElementById('memoryChips'); const log = document.getElementById('memoryLog');
  if (!grid || !log) return;
  grid.innerHTML = state.memory.map((item, index) => `<span class="memory-chip">${esc(item)}<button data-memory-remove="${index}" aria-label="Remove memory">×</button></span>`).join('') || '<span class="search-empty">No active memories.</span>';
  log.innerHTML = state.memoryLog.map(item => `<div class="memory-log-item ${item.tone}"><i></i><div><p>${esc(item.text)}</p><small>${esc(item.time)}</small></div></div>`).join('');
}

function renderLoaderSteps(active = -1, loading = -1) {
  const steps = ['Extract text', 'Find skills', 'Score ATS', 'Build twin'];
  document.getElementById('loaderSteps').innerHTML = steps.map((step, index) => `<div class="loader-step ${index <= active ? 'active' : ''} ${index === loading ? 'loading' : ''}"><span>${index < active ? '✓' : index + 1}</span>${step}</div>`).join('');
}

async function uploadResumeToApi() {
  const file = document.getElementById('resumeFile')?.files?.[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  try {
    const result = await apiRequest('/resume/parse', { method: 'POST', body: form });
    const twin = result.resume_json || {};
    if (Array.isArray(twin.skills) && twin.skills.length) state.skills = twin.skills;
    state.ats = result.ats_score || state.ats;
    document.getElementById('resumeJson').textContent = JSON.stringify(twin, null, 2);
    document.getElementById('bigScore').textContent = state.ats;
    document.getElementById('atsDelta').textContent = `${result.gaps?.length || 0} open skill gaps`;
    renderChips();
    toast('Profiler agent synced · twin memory updated', 'success');
  } catch (error) {
    // The deterministic local loader remains the fallback when the API is offline.
  }
}

function parseResume() {
  const status = document.getElementById('loaderStatus'); const button = document.getElementById('parseBtn');
  if (button.disabled) return;
  button.disabled = true; button.style.opacity = '.65';
  const steps = ['Extracting text', 'Finding skills', 'Scoring ATS', 'Building twin'];
  let current = 0; renderLoaderSteps(-1, 0); status.textContent = steps[0];
  const timer = window.setInterval(() => {
    renderLoaderSteps(current - 1, current < steps.length ? current : -1);
    if (current < steps.length) status.textContent = steps[current];
    current += 1;
    if (current > steps.length) {
      window.clearInterval(timer); renderLoaderSteps(steps.length); status.textContent = 'Twin ready · memory grounded'; button.disabled = false; button.style.opacity = '1';
      state.ats = 82; state.skills = ['React', 'Python', 'SQL', 'Tailwind'];
      const payload = { name: document.getElementById('pName')?.value || 'Sudipta Samanta', skills: state.skills, education: ['B.Tech CSE'], experience: ['Intern · TCS'], ats: state.ats, strengths: ['React product delivery', 'Problem solving'], gaps: ['Docker', 'Kubernetes'], recommendation: 'Add Docker → 94%' };
      document.getElementById('resumeJson').textContent = JSON.stringify(payload, null, 2);
      document.getElementById('scoreHeadline').textContent = 'Promising, with room to compound.';
      document.getElementById('scoreSubline').textContent = 'A strong React base. One practical cloud skill unlocks more roles.';
      document.getElementById('atsDelta').textContent = '+14 with Docker';
      renderChips();
      state.memoryLog.unshift({ text: 'Parsed resume and refreshed twin skills', time: 'Just now · local demo', tone: 'green' });
      renderProfile();
      toast('Twin built · ATS signal updated', 'success');
      uploadResumeToApi();
    }
  }, 520);
}

function openExplain(id) {
  const item = JOBS.find(job => job.id === id) || state.api.feedItems?.find(job => job.id === id);
  if (!item) return;
  const detail = item.detail || hybrid(item);
  document.getElementById('explainTitle').textContent = `Why you see this · ${item.title}`;
  const rows = [['Relevance', detail.relevance], ['Skill overlap', detail.skillOverlap], ['Social path', detail.social], ['Freshness', detail.freshness], ['Hate penalty avoided', 1 - detail.hatePenalty]];
  document.getElementById('explainBody').innerHTML = rows.map(([label, value]) => `<div class="explain-row"><label>${label}</label><div class="explain-bar"><span style="width:${Math.round(value * 100)}%;background:${label === 'Hate penalty avoided' ? 'var(--green)' : 'var(--saffron)'}"></span></div><b>${Math.round(value * 100)}%</b></div>`).join('') + `<div class="counterfactual"><strong>Counterfactual:</strong> add <b>Docker</b> and <b>Kubernetes</b> to move your twin from <b>82%</b> to <b>94%</b>. If Priya refers you, the social signal adds another <b>+5</b>.</div>`;
  openModal('explainSheet');
}

function openShareSheet(title = state.shareTitle, id = 'signal') {
  state.shareTitle = title;
  state.shareUrl = `https://bharatcareertwin.local/${id}`;
  document.getElementById('shareTitle').textContent = title;
  document.getElementById('sharePreviewTitle').textContent = title;
  document.getElementById('shareUrl').value = state.shareUrl;
  openModal('shareSheet');
  drawQr();
}

function drawQr() {
  const canvas = document.getElementById('shareCanvas'); const fallback = document.getElementById('qrFallback');
  if (!canvas) return;
  fallback.style.display = 'none';
  if (window.QRCode?.toCanvas) {
    window.QRCode.toCanvas(canvas, state.shareUrl, { width: 146, margin: 1, color: { dark: '#142018', light: '#ffffff' } }, error => { if (error) fallback.style.display = 'grid'; });
  } else {
    fallback.style.display = 'grid';
    const ctx = canvas.getContext('2d'); ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#142018';
    for (let row = 0; row < 21; row += 1) for (let col = 0; col < 21; col += 1) if ((row * 17 + col * 11 + state.shareUrl.length) % 3 === 0 || (row < 7 && col < 7) || (row > 13 && col < 7) || (row < 7 && col > 13)) ctx.fillRect(col * 7, row * 7, 5, 5);
  }
}

function openShare(platform) {
  const url = encodeURIComponent(state.shareUrl); const title = encodeURIComponent(state.shareTitle);
  const targets = { wa: `https://wa.me/?text=${title}%20${url}`, tw: `https://twitter.com/intent/tweet?text=${title}&url=${url}`, li: `https://www.linkedin.com/sharing/share-offsite/?url=${url}` };
  window.open(targets[platform], '_blank', 'noopener,noreferrer');
}

function copyText(value, message = 'Copied to clipboard') {
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(value).catch(() => fallbackCopy(value)); else fallbackCopy(value);
  toast(message, 'success');
}

function fallbackCopy(value) {
  const temp = document.createElement('textarea'); temp.value = value; temp.style.position = 'fixed'; temp.style.opacity = '0'; document.body.appendChild(temp); temp.select(); document.execCommand('copy'); temp.remove();
}

function downloadQr() {
  const canvas = document.getElementById('shareCanvas');
  if (!canvas) return;
  const link = document.createElement('a'); link.download = 'bharat-career-twin-qr.png'; link.href = canvas.toDataURL('image/png'); link.click(); toast('QR downloaded · share it with your circle', 'success');
}

function renderReferral() {
  const path = document.getElementById('referralPath');
  const pathNodes = state.referralPath || [{ name: 'You', relation: 'self' }, { name: 'Priya · TCS', relation: 'mutual · 1 hop' }, { name: 'Aman · hiring', relation: 'company · 2 hops' }];
  path.innerHTML = pathNodes.map((node, index) => `${index ? '<span class="path-arrow">→</span>' : ''}<span class="path-node ${index === 0 ? 'you' : ''}"><i class="path-avatar">${esc(node.name.charAt(0))}</i>${esc(node.name)}</span>`).join('');
  const message = state.referralDrafts ? (state.referralLanguage === 'hinglish' ? state.referralDrafts.hinglish : state.referralDrafts.english) : state.referralLanguage === 'hinglish' ? 'Hi Priya — Sudipta here. I’m exploring the React role at TCS. Aapka work in product teams stood out; would you be open to a quick referral if the profile feels relevant?' : 'Hi Priya — I’m exploring the React role at TCS. Your work in product teams stood out; would you be open to a quick referral if the profile feels relevant?';
  document.getElementById('referralMessage').textContent = message;
  document.querySelectorAll('[data-referral-language]').forEach(button => button.classList.toggle('active', button.dataset.referralLanguage === state.referralLanguage));
}

async function openReferral() {
  renderReferral();
  openModal('referralModal');
  try {
    const result = await apiRequest('/peers/referral-path?job_id=j1');
    state.referralPath = result.path;
    state.referralDrafts = { hinglish: result.draft_hinglish, english: result.draft_english };
    renderReferral();
  } catch (error) { /* local path remains visible when the API is offline */ }
}

function renderSearch(query = '') {
  const normalized = query.trim().toLowerCase();
  const entries = [
    ...JOBS.map(job => ({ id: job.id, title: job.title, meta: `${job.company} · ${job.location}`, type: 'job', route: 'feed', icon: '↗' })),
    ...SCHEMES.map(scheme => ({ id: scheme.id, title: scheme.name, meta: `${scheme.ministry} · scheme`, type: 'scheme', route: 'schemes', icon: '₹' })),
    ...PEERS.map(peer => ({ id: peer.id, title: peer.name, meta: `${peer.role} · ${peer.dist} km`, type: 'peer', route: 'peers', icon: '●' })),
    ...STARTUPS.map(startup => ({ id: startup.id, title: startup.title, meta: `${startup.cat} · ${startup.owner}`, type: 'startup', route: 'startups', icon: '✦' })),
  ].filter(entry => !normalized || `${entry.title} ${entry.meta}`.toLowerCase().includes(normalized)).slice(0, 10);
  state.selectedSearch = Math.min(state.selectedSearch, Math.max(0, entries.length - 1));
  const results = document.getElementById('searchResults');
  results.innerHTML = entries.length ? entries.map((entry, index) => `<button class="search-result ${index === state.selectedSearch ? 'selected' : ''}" data-search-route="${entry.route}" data-search-id="${entry.id}"><span class="search-result-icon">${entry.icon}</span><span class="search-result-copy"><strong>${esc(entry.title)}</strong><span>${esc(entry.meta)}</span></span><span class="search-result-arrow">↗</span></button>`).join('') : '<div class="search-empty">No signal found. Try a skill, city or “scheme”.</div>';
}

function runSimulation() {
  const input = document.getElementById('simulationInput').value.trim();
  const root = document.getElementById('simulationResults');
  const local = /local|nagpur|near/.test(input.toLowerCase()); const study = /study|course|learn/.test(input.toLowerCase()); const startup = /founder|startup|idea/.test(input.toLowerCase());
  const rows = [
    ['Local roles', local ? '+18%' : '+4%', local ? 'green' : ''],
    ['Skill-matched jobs', study ? '+11%' : '+8%', ''],
    ['New perspectives', startup ? '+15%' : '+9%', 'green'],
    ['Echo-chamber risk', input.includes('fewer') ? '−12%' : '−4%', 'green'],
  ];
  root.innerHTML = rows.map(row => `<div class="simulation-result"><strong>${row[0]}</strong><span class="${row[2]}">${row[1]} in preview</span></div>`).join('') + '<div class="counterfactual">This is a preview only. Apply it from the feed if it still feels like you.</div>';
}

function drawGraph() {
  const canvas = document.getElementById('graphCanvas'); if (!canvas) return;
  let ctx;
  try { ctx = canvas.getContext('2d'); } catch (error) { return; }
  if (!ctx) return;
  const rect = canvas.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1; const width = Math.max(600, rect.width || 900); const height = 330;
  canvas.width = width * ratio; canvas.height = height * ratio; ctx.scale(ratio, ratio); ctx.clearRect(0, 0, width, height);
  const center = { x: width * .5, y: height * .52 }; const nodes = PEERS.map((peer, index) => ({ peer, x: width * (.16 + (index % 3) * .34) + Math.sin(index) * 25, y: height * (.2 + Math.floor(index / 3) * .55) + Math.cos(index * 2) * 18 }));
  ctx.lineWidth = 1; nodes.forEach((node, index) => { ctx.strokeStyle = index % 2 ? 'rgba(80,118,168,.35)' : 'rgba(21,107,72,.32)'; ctx.beginPath(); ctx.moveTo(center.x, center.y); ctx.lineTo(node.x, node.y); ctx.stroke(); });
  ctx.setLineDash([4, 5]); ctx.strokeStyle = 'rgba(242,107,58,.35)'; ctx.beginPath(); ctx.moveTo(nodes[0].x, nodes[0].y); ctx.lineTo(nodes[2].x, nodes[2].y); ctx.stroke(); ctx.setLineDash([]);
  ctx.font = '600 10px DM Sans'; ctx.textAlign = 'center'; nodes.forEach(node => { ctx.fillStyle = node.peer.color; ctx.beginPath(); ctx.arc(node.x, node.y, 13, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = '#fff'; ctx.fillText(node.peer.name.charAt(0), node.x, node.y + 3.5); ctx.fillStyle = '#66736a'; ctx.fillText(node.peer.name.split(' ')[0], node.x, node.y + 28); });
  ctx.fillStyle = '#f26b3a'; ctx.beginPath(); ctx.arc(center.x, center.y, 18, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = '800 10px DM Sans'; ctx.fillText('YOU', center.x, center.y + 3.5);
}

function bindEvents() {
  document.addEventListener('click', event => {
    const routeTarget = event.target.closest('[data-route]');
    if (routeTarget) { go(routeTarget.dataset.route); return; }
    const actionTarget = event.target.closest('[data-action]');
    if (actionTarget) {
      const action = actionTarget.dataset.action;
      if (action === 'open-search') openSearch();
      if (action === 'open-share') openShareSheet(actionTarget.dataset.title || state.shareTitle, actionTarget.dataset.id || 'signal');
      if (action === 'open-referral') openReferral();
      if (action === 'open-simulation') openModal('simulationModal');
      return;
    }
    const tab = event.target.closest('[data-tab]'); if (tab) { state.tab = tab.dataset.tab; renderFeed(); return; }
    const steer = event.target.closest('[data-steer]'); if (steer) { document.getElementById('steerInput').value = steer.dataset.steer; applySteer(); return; }
    const focus = event.target.closest('[data-focus]'); if (focus) { setFocus(focus.dataset.focus); return; }
    const profileFocus = event.target.closest('[data-profile-focus]'); if (profileFocus) { setFocus(profileFocus.dataset.profileFocus); return; }
    const dnaInterest = event.target.closest('[data-dna-interest]'); if (dnaInterest) { const value = dnaInterest.dataset.dnaInterest; state.interests = state.interests.includes(value) ? state.interests.filter(item => item !== value) : [...state.interests, value]; renderChips(); renderFeed(); return; }
    const dnaHate = event.target.closest('[data-dna-hate]'); if (dnaHate) { const value = dnaHate.dataset.dnaHate; state.hates = state.hates.includes(value) ? state.hates.filter(item => item !== value) : [...state.hates, value]; renderChips(); renderFeed(); return; }
    const cardAction = event.target.closest('[data-card-action]');
    if (cardAction) { handleCardAction(cardAction.dataset.cardAction, cardAction.dataset.id, cardAction.dataset.title); return; }
    const searchResult = event.target.closest('[data-search-route]');
    if (searchResult) { closeModal('searchModal'); go(searchResult.dataset.searchRoute); return; }
    const memoryRemove = event.target.closest('[data-memory-remove]'); if (memoryRemove) { state.memory.splice(Number(memoryRemove.dataset.memoryRemove), 1); renderProfile(); toast('Memory removed'); return; }
    const referralLanguage = event.target.closest('[data-referral-language]'); if (referralLanguage) { state.referralLanguage = referralLanguage.dataset.referralLanguage; renderReferral(); return; }
    const preset = event.target.closest('[data-simulation]'); if (preset) { document.getElementById('simulationInput').value = preset.dataset.simulation; runSimulation(); return; }
    const closeOnBackdrop = event.target.closest('.modal-layer');
    if (closeOnBackdrop && event.target === closeOnBackdrop) closeModal(closeOnBackdrop.id);
  });

  document.getElementById('collapseSidebar').addEventListener('click', () => document.body.classList.toggle('sidebar-collapsed'));
  document.getElementById('mobileMenu').addEventListener('click', () => { document.getElementById('sidebar').classList.add('mobile-open'); document.getElementById('mobileBackdrop').classList.add('visible'); });
  document.getElementById('mobileBackdrop').addEventListener('click', () => { document.getElementById('sidebar').classList.remove('mobile-open'); document.getElementById('mobileBackdrop').classList.remove('visible'); });
  document.getElementById('searchBtn').addEventListener('click', openSearch);
  document.getElementById('bellBtn').addEventListener('click', () => { go('feed'); toast('Digest ready · 3 signals worth your attention', 'success'); });
  document.getElementById('langBtn').addEventListener('click', () => { state.lang = state.lang === 'EN' ? 'HI' : 'EN'; toast(state.lang === 'HI' ? 'Hinglish mode on · namaste' : 'English mode on', 'success'); });
  document.getElementById('steerSubmit').addEventListener('click', applySteer);
  document.getElementById('steerInput').addEventListener('keydown', event => { if (event.key === 'Enter') applySteer(); });
  document.getElementById('resetDNA').addEventListener('click', () => { state.interests = ['React', 'AI/ML', 'Product']; state.hates = []; state.steer = 'more coding roles, less night shift'; document.getElementById('steerInput').value = state.steer; renderChips(); renderFeed(); toast('Memory reset · feed widened', 'success'); });
  document.getElementById('loadMore').addEventListener('click', () => { state.limit += 3; renderFeed(); });
  document.getElementById('peerSkill').addEventListener('input', renderPeers); document.getElementById('peerRadius').addEventListener('change', renderPeers);
  document.getElementById('eligibleOnly').addEventListener('change', renderSchemes);
  document.getElementById('graphToggle').addEventListener('click', () => { const graph = document.getElementById('graphView'); const visible = graph.classList.toggle('visible'); document.getElementById('graphToggleLabel').textContent = visible ? 'Hide graph' : 'Graph view'; if (visible) drawGraph(); });
  document.getElementById('newIdeaBtn').addEventListener('click', () => document.getElementById('newIdeaForm').classList.add('visible'));
  document.getElementById('closeIdeaForm').addEventListener('click', () => document.getElementById('newIdeaForm').classList.remove('visible'));
  document.getElementById('createIdea').addEventListener('click', createIdea);
  document.getElementById('syncBtn').addEventListener('click', () => toast('freehire sync preview · 45 inserted, 12 updated', 'success'));
  document.getElementById('resumeFile').addEventListener('change', event => { const file = event.target.files?.[0]; document.getElementById('fileName').textContent = file ? file.name : 'No file selected'; if (file) toast('Resume ready · parse when you are', 'success'); });
  const uploadZone = document.getElementById('uploadZone'); ['dragenter', 'dragover'].forEach(type => uploadZone.addEventListener(type, event => { event.preventDefault(); uploadZone.classList.add('dragging'); })); ['dragleave', 'drop'].forEach(type => uploadZone.addEventListener(type, event => { event.preventDefault(); uploadZone.classList.remove('dragging'); })); uploadZone.addEventListener('drop', event => { const file = event.dataTransfer.files?.[0]; if (file) { document.getElementById('fileName').textContent = file.name; toast('Resume ready · parse when you are', 'success'); } });
  document.getElementById('parseBtn').addEventListener('click', parseResume);
  document.getElementById('addSql').addEventListener('click', () => { state.ats = Math.min(94, state.ats + 7); if (!state.skills.includes('SQL')) state.skills.push('SQL'); renderChips(); toast(`SQL added · ATS ${state.ats}%`, 'success'); });
  document.getElementById('copyResumeJson').addEventListener('click', () => copyText(document.getElementById('resumeJson').textContent, 'Twin JSON copied'));
  document.getElementById('copyCover').addEventListener('click', () => copyText(document.getElementById('cover').value, 'Cover letter copied'));
  document.getElementById('downloadTwin').addEventListener('click', () => { const blob = new Blob([document.getElementById('resumeJson').textContent], { type: 'application/json' }); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'bharat-career-twin.json'; link.click(); URL.revokeObjectURL(link.href); toast('Twin JSON downloaded', 'success'); });
  document.getElementById('copyBtn').addEventListener('click', () => copyText(state.shareUrl, 'Link copied · ready for WhatsApp'));
  document.getElementById('downloadQr').addEventListener('click', downloadQr);
  document.querySelectorAll('[data-share]').forEach(button => button.addEventListener('click', () => openShare(button.dataset.share)));
  document.getElementById('closeSearch').addEventListener('click', () => closeModal('searchModal')); document.getElementById('closeShare').addEventListener('click', () => closeModal('shareSheet')); document.getElementById('closeExplain').addEventListener('click', () => closeModal('explainSheet')); document.getElementById('closeReferral').addEventListener('click', () => closeModal('referralModal')); document.getElementById('closeSimulation').addEventListener('click', () => closeModal('simulationModal'));
  document.getElementById('searchInput').addEventListener('input', event => { state.selectedSearch = 0; renderSearch(event.target.value); });
  document.getElementById('runSimulation').addEventListener('click', runSimulation);
  document.getElementById('copyReferral').addEventListener('click', () => copyText(document.getElementById('referralMessage').textContent, 'Referral message copied'));
  document.getElementById('referralShareBtn').addEventListener('click', () => openShareSheet('Warm referral path · Sudipta → Priya → TCS', 'referral-path'));
  document.getElementById('addMemory').addEventListener('click', addMemory); document.getElementById('memoryInput').addEventListener('keydown', event => { if (event.key === 'Enter') addMemory(); });
  document.getElementById('clearMemory').addEventListener('click', () => { state.memory = []; state.memoryLog.unshift({ text: 'Cleared editable memory', time: 'Just now · local demo', tone: '' }); renderProfile(); toast('Memory cleared · fresh start', 'success'); });
  document.getElementById('saveProfile').addEventListener('click', () => { state.memoryLog.unshift({ text: `Saved profile from ${document.getElementById('pCity').value}`, time: 'Just now · local demo', tone: 'green' }); renderProfile(); toast('Profile changes saved', 'success'); });
  document.addEventListener('keydown', event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); openSearch(); } if (event.key === 'Escape') closeAllModals(); if (document.getElementById('searchModal').classList.contains('visible')) { const items = [...document.querySelectorAll('.search-result')]; if (event.key === 'ArrowDown') { event.preventDefault(); state.selectedSearch = Math.min(items.length - 1, state.selectedSearch + 1); renderSearch(document.getElementById('searchInput').value); } if (event.key === 'ArrowUp') { event.preventDefault(); state.selectedSearch = Math.max(0, state.selectedSearch - 1); renderSearch(document.getElementById('searchInput').value); } if (event.key === 'Enter' && items[state.selectedSearch]) { event.preventDefault(); items[state.selectedSearch].click(); } } });
  window.addEventListener('resize', () => { if (document.getElementById('graphView')?.classList.contains('visible')) drawGraph(); });
}

function handleCardAction(action, id, title) {
  const apiItem = state.api.feedItems?.find(item => item.id === id);
  const itemType = apiItem?.type || 'job';
  if (action === 'share') { sendInteraction('share', id, itemType); openShareSheet(title || 'Bharat Career Twin signal', id); }
  if (action === 'why') openExplain(id);
  if (action === 'referral') { sendInteraction('view', id, itemType); openReferral(); }
  if (action === 'apply') { sendInteraction('apply', id, itemType); toast('Application tracked · keep your story ready', 'success'); }
  if (action === 'connect') { sendInteraction('view', id, itemType); toast('Connection request drafted · be specific and kind', 'success'); }
  if (action === 'help') { sendInteraction('apply', id, itemType); toast('Builder signal sent · your twin is on the shortlist', 'success'); }
  if (action === 'open-scheme') { go('schemes'); toast('Eligibility details opened', 'success'); }
  if (action === 'like') { sendInteraction('like', id, itemType); const job = JOBS.find(item => item.id === id); if (job) job.likes += 1; toast('Liked · interest +2', 'success'); renderCurrentFeedCards(); }
  if (action === 'save') { sendInteraction('save', id, itemType); const job = JOBS.find(item => item.id === id); if (job) job.saves += 1; toast('Saved · interest +3', 'success'); }
  if (action === 'hide') { sendInteraction('hide', id, itemType, 'Night shift'); const index = JOBS.findIndex(item => item.id === id); if (index > -1) JOBS.splice(index, 1); if (state.api.feedItems) state.api.feedItems = state.api.feedItems.filter(item => item.id !== id); state.hates = [...new Set([...state.hates, 'Night shift'])]; toast('Hidden · boundary remembered', 'success'); renderCurrentFeedCards(); }
}

function applySteer() {
  const input = document.getElementById('steerInput'); const value = input.value.trim(); if (!value) return;
  state.steer = value; state.diversity = Math.max(52, Math.min(84, 72 + (value.includes('less') ? 4 : 0))); document.getElementById('steerFeedback').innerHTML = `<i></i><span>Agent memory updated · ${value.toLowerCase().includes('nagpur') ? 'local roles moved up' : 'feed weights refreshed'}</span>`; state.tab = 'all'; renderFeed(); toast('Steer applied · feed reranked', 'success');
}

function setFocus(focus) {
  state.focus = focus; const note = document.getElementById('focusNote'); if (note) note.textContent = focus === 'study' ? 'Free courses and skill gaps are up front' : focus === 'relax' ? 'A wider, lower-pressure view' : 'Balanced for your next job move'; document.querySelectorAll('[data-focus]').forEach(button => button.classList.toggle('active', button.dataset.focus === focus)); document.querySelectorAll('[data-profile-focus]').forEach(button => button.classList.toggle('active', button.dataset.profileFocus === focus)); renderFeed(); toast(`${focus === 'study' ? 'Study' : focus === 'relax' ? 'Reset' : 'Career'} mode on`, 'success');
}

function createIdea() {
  const title = document.getElementById('ideaTitle').value.trim(); const desc = document.getElementById('ideaDesc').value.trim(); const skills = document.getElementById('ideaSkills').value.split(',').map(item => item.trim()).filter(Boolean);
  if (title.length < 10) return toast('Give the idea a little more shape'); if (desc.length < 40) return toast('Tell the story in at least one clear paragraph'); if (!skills.length) return toast('Add one skill you need');
  STARTUPS.unshift({ id: `st${Date.now()}`, title, desc, need: skills, match: .84, likes: 0, owner: 'You', cat: 'Custom' }); document.getElementById('ideaTitle').value = ''; document.getElementById('ideaDesc').value = ''; document.getElementById('ideaSkills').value = ''; document.getElementById('newIdeaForm').classList.remove('visible'); renderStartups();
  apiRequest('/startups', { method: 'POST', body: JSON.stringify({ title, description: desc, category: 'Custom', skills_needed: skills, location_city: document.getElementById('pCity')?.value || 'Nagpur' }) }).catch(() => {});
  toast('Idea published · matching builders', 'success');
}

function addMemory() {
  const input = document.getElementById('memoryInput'); const value = input.value.trim(); if (!value) return; state.memory.unshift(value); state.memoryLog.unshift({ text: `Added “${value}”`, time: 'Just now · local demo', tone: '' }); input.value = ''; renderProfile(); toast('Memory added · you are still in control', 'success');
}

function mountTeamReveal() {
  const agents = [
    ['01', 'Profiler', 'Resume → a living skill map', 'P', '#f26b3a', '#fff1e9'], ['02', 'Interest miner', 'Likes, hides and honest boundaries', 'I', '#156b48', '#eaf5ed'], ['03', 'Matcher', 'Roles and schemes with receipts', 'M', '#5076a8', '#edf4fb'], ['04', 'Social connector', 'Warm paths, not cold outreach', 'S', '#b86e78', '#f9ecee'], ['05', 'Coach gap', 'The smallest skill unlock', 'C', '#9b710d', '#fff5d8'], ['06', 'Feed ranker', 'Variety without losing relevance', 'R', '#7d67a6', '#f2edfb'],
  ];
  document.getElementById('teamRevealGrid').innerHTML = agents.map((agent, index) => `<article class="team-card ${index === 0 ? 'active' : ''}" style="--team-color:${agent[4]};--team-tint:${agent[5]}" data-team-index="${index}"><div class="team-card-top"><span class="team-avatar">${agent[3]}</span><span class="team-number">${agent[0]} / 06</span></div><div><h3>${agent[1]}</h3><p>${agent[2]}</p><div class="team-reveal"><span></span> ${index === 0 ? 'revealing now' : 'hover to reveal'}</div></div></article>`).join('');
  let active = 0; window.setInterval(() => { const cards = [...document.querySelectorAll('.team-card')]; if (!cards.length || state.activeRoute !== 'landing') return; cards.forEach(card => { card.classList.remove('active'); card.querySelector('.team-reveal').innerHTML = '<span></span> hover to reveal'; }); active = (active + 1) % cards.length; cards[active].classList.add('active'); cards[active].querySelector('.team-reveal').innerHTML = '<span></span> revealing now'; }, 2500);
}

let appMounted = false;
document.addEventListener('DOMContentLoaded', () => {
  if (appMounted) return;
  appMounted = true;
  buildNav(); updateBreadcrumb('landing'); renderLoaderSteps(); renderChips(); renderDigest(); renderProfile(); renderReferral(); renderFeed(); mountTeamReveal(); bindEvents(); loadModelStatus();
  window.go = go; window.toast = toast; window.openShareSheet = openShareSheet; window.openReferral = openReferral; window.openExplain = openExplain;
});
