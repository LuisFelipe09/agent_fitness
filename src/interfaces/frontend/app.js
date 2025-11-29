// API Base URL
const API_BASE = "";

// Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();
tg.enableClosingConfirmation();
tg.disableVerticalSwipes(); // Disable swipe-to-close to allow scrolling

const userId = tg.initDataUnsafe?.user?.id ? String(tg.initDataUnsafe.user.id) : "test_user";
const username = tg.initDataUnsafe?.user?.username || "Test User";

// State
let currentPlan = null;
let currentPlanType = null;

// Initialize
async function init() {
    // Register user
    await fetch(`${API_BASE}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: userId, username: username })
    });

    // Load notifications
    loadNotifications();

    // Setup UI
    setupEventListeners();
}

function setupEventListeners() {
    document.getElementById('notification-bell').addEventListener('click', toggleNotifications);
}

// === NOTIFICATIONS ===

async function loadNotifications() {
    try {
        const res = await fetch(`${API_BASE}/notifications?unread_only=true`, {
            headers: { 'X-User-Id': userId }
        });
        const notifications = await res.json();
        updateNotificationBadge(notifications.length);
        renderNotifications(notifications);
    } catch (e) {
        console.error("Error loading notifications", e);
    }
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notification-count');
    if (count > 0) {
        badge.innerText = count;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function renderNotifications(notifications) {
    const container = document.getElementById('notification-list');
    container.innerHTML = '';

    if (notifications.length === 0) {
        container.innerHTML = '<div class="notification-item">No new notifications</div>';
        return;
    }

    notifications.forEach(n => {
        const div = document.createElement('div');
        div.className = `notification-item ${n.is_read ? '' : 'unread'}`;
        div.innerHTML = `
            <strong>${n.title}</strong>
            <p>${n.message}</p>
            <small>${new Date(n.created_at).toLocaleString()}</small>
            <button class="secondary" onclick="markRead('${n.id}')" style="padding: 2px 8px; font-size: 12px; width: auto; margin-top: 5px;">Mark Read</button>
        `;
        container.appendChild(div);
    });
}

function toggleNotifications() {
    const dropdown = document.getElementById('notification-dropdown');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

async function markRead(id) {
    await fetch(`${API_BASE}/notifications/${id}/read`, {
        method: 'PATCH',
        headers: { 'X-User-Id': userId }
    });
    loadNotifications();
}

// === PLANS ===

async function generateWorkout() {
    showLoading();
    try {
        const res = await fetch(`${API_BASE}/users/${userId}/plans/workout`, { method: 'POST' });
        const plan = await res.json();
        displayPlan(plan, 'workout');
    } catch (e) {
        alert("Error generating plan");
    }
}

async function generateNutrition() {
    showLoading();
    try {
        const res = await fetch(`${API_BASE}/users/${userId}/plans/nutrition`, { method: 'POST' });
        const plan = await res.json();
        displayPlan(plan, 'nutrition');
    } catch (e) {
        alert("Error generating plan");
    }
}

function displayPlan(plan, type) {
    currentPlan = plan;
    currentPlanType = type;

    const container = document.getElementById('result-content');
    const resultSection = document.getElementById('result');

    // Badge
    const badgeClass = `badge-${plan.state || 'draft'}`;
    const badgeHtml = `<span class="badge ${badgeClass}">${plan.state || 'DRAFT'}</span>`;

    // Content
    let contentHtml = '';
    if (type === 'workout') {
        contentHtml = plan.sessions.map(s => `
            <div class="card">
                <h3>${s.day} - ${s.focus}</h3>
                <ul>${s.exercises.map(e => `<li>${e.name}: ${e.sets}x${e.reps}</li>`).join('')}</ul>
            </div>
        `).join('');
    } else {
        contentHtml = plan.daily_plans.map(d => `
            <div class="card">
                <h3>${d.day}</h3>
                <ul>${d.meals.map(m => `<li>${m.name} (${m.calories} kcal)</li>`).join('')}</ul>
            </div>
        `).join('');
    }

    // Traceability
    const metaHtml = `
        <div style="margin-bottom: 15px; font-size: 12px; color: #666;">
            Created by: ${plan.created_by || 'Unknown'}<br>
            Last modified: ${plan.modified_at ? new Date(plan.modified_at).toLocaleString() : 'Never'}
            ${plan.modified_by ? `by ${plan.modified_by}` : ''}
        </div>
    `;

    // Comments Section
    const commentsHtml = `
        <div class="comments-section">
            <h3>Comments</h3>
            <div id="comments-list">Loading comments...</div>
            <textarea id="new-comment" class="comment-input" placeholder="Add a comment..."></textarea>
            <button onclick="addComment()">Post Comment</button>
        </div>
    `;

    // Versions Link
    const versionsHtml = `
        <div style="margin-top: 10px;">
            <button class="secondary" onclick="loadVersions('${plan.id}')">View Version History</button>
            <div id="versions-list" class="hidden"></div>
        </div>
    `;

    container.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h2>Your Plan</h2>
            ${badgeHtml}
        </div>
        ${metaHtml}
        ${contentHtml}
        ${versionsHtml}
        ${commentsHtml}
    `;

    resultSection.classList.remove('hidden');
    loadComments(plan.id);
}

// === COMMENTS ===

async function loadComments(planId) {
    const res = await fetch(`${API_BASE}/plans/${planId}/comments`, {
        headers: { 'X-User-Id': userId }
    });
    const comments = await res.json();

    const container = document.getElementById('comments-list');
    if (comments.length === 0) {
        container.innerHTML = '<p>No comments yet.</p>';
        return;
    }

    container.innerHTML = comments.map(c => `
        <div class="comment ${c.is_internal ? 'internal' : ''}">
            <div class="comment-header">
                <strong>${c.author_role}</strong>
                <span>${new Date(c.created_at).toLocaleString()}</span>
            </div>
            <div>${c.content}</div>
        </div>
    `).join('');
}

async function addComment() {
    const content = document.getElementById('new-comment').value;
    if (!content) return;

    await fetch(`${API_BASE}/plans/${currentPlan.id}/comments?plan_type=${currentPlanType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-User-Id': userId
        },
        body: JSON.stringify({ content, is_internal: false })
    });

    document.getElementById('new-comment').value = '';
    loadComments(currentPlan.id);
}

// === VERSIONS ===

async function loadVersions(planId) {
    const container = document.getElementById('versions-list');
    container.classList.remove('hidden');
    container.innerHTML = 'Loading...';

    const res = await fetch(`${API_BASE}/plans/${planId}/versions`, {
        headers: { 'X-User-Id': userId }
    });
    const versions = await res.json();

    if (versions.length === 0) {
        container.innerHTML = '<p>No history available.</p>';
        return;
    }

    container.innerHTML = versions.map(v => `
        <div class="version-item">
            <span>v${v.version_number} - ${v.changes_summary || 'Update'}</span>
            <span>${new Date(v.created_at).toLocaleDateString()}</span>
        </div>
    `).join('');
}

// === UTILS ===

function showLoading() {
    document.getElementById('result').classList.remove('hidden');
    document.getElementById('result-content').innerHTML = '<div style="text-align:center; padding:20px;">Generating...</div>';
}

function saveProfile() {
    const profile = {
        age: parseInt(document.getElementById('age').value),
        weight: parseFloat(document.getElementById('weight').value),
        height: parseFloat(document.getElementById('height').value),
        gender: document.getElementById('gender').value,
        goal: document.getElementById('goal').value,
        activity_level: document.getElementById('activity_level').value,
        dietary_restrictions: [],
        injuries: []
    };

    fetch(`${API_BASE}/users/${userId}/profile`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-User-Id': userId
        },
        body: JSON.stringify(profile)
    })
        .then(response => {
            if (response.ok) {
                alert("Profile saved!");
                document.getElementById('actions').classList.remove('hidden');
            } else {
                alert("Error saving profile");
            }
        });
}

function togglePasswordForm() {
    const form = document.getElementById('password-form');
    form.classList.toggle('hidden');
}

async function setWebPassword() {
    const email = document.getElementById('web-email').value;
    const password = document.getElementById('web-password').value;

    if (!password) {
        alert("Password is required");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/auth/set-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': userId
            },
            body: JSON.stringify({
                email: email || null,
                password: password
            })
        });

        if (res.ok) {
            alert("Password set successfully! You can now login via web.");
            document.getElementById('password-form').classList.add('hidden');
            document.getElementById('web-password').value = '';
        } else {
            const err = await res.json();
            alert(`Error: ${err.detail}`);
        }
    } catch (e) {
        alert("Error setting password");
        console.error(e);
    }
}

// Start
init();
