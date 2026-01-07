/**
 * Hotel PMS - Admin Dashboard JavaScript
 * Connected to Backend API with fallback to mock data
 */

// ============================================
// Configuration
// ============================================

const API_BASE_URL = 'http://localhost:8000/api/v1';
let USE_MOCK_DATA = true; // Will be set to false if API is available

// ============================================
// API Client
// ============================================

async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.warn(`API request failed: ${endpoint}`, error);
        throw error;
    }
}

async function checkApiConnection() {
    try {
        const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
            method: 'GET',
            timeout: 3000
        });

        if (response.ok) {
            USE_MOCK_DATA = false;
            console.log('✅ Connected to Backend API');
            showToast('Connected to Backend API', 'success');
            return true;
        }
    } catch (error) {
        console.log('⚠️ Backend not available, using mock data');
        USE_MOCK_DATA = true;
    }
    return false;
}

// ============================================
// Mock Data (fallback when API unavailable)
// ============================================

const mockData = {
    stats: {
        totalBookings: 12,
        todayCheckins: 3,
        todayCheckouts: 2,
        occupancyRate: 78
    },

    bookings: [
        {
            id: 1,
            channexId: 'channex_001',
            guest: 'John Smith',
            nationality: 'United States',
            room: '101',
            checkin: '2026-01-08',
            checkout: '2026-01-11',
            ota: 'airbnb',
            status: 'confirmed',
            passcode: '123456'
        },
        {
            id: 2,
            channexId: 'channex_002',
            guest: 'Marie Dupont',
            nationality: 'France',
            room: '102',
            checkin: '2026-01-09',
            checkout: '2026-01-12',
            ota: 'booking',
            status: 'confirmed',
            passcode: '654321'
        },
        {
            id: 3,
            channexId: 'channex_003',
            guest: 'Tanaka Yuki',
            nationality: 'Japan',
            room: '201',
            checkin: '2026-01-07',
            checkout: '2026-01-10',
            ota: 'agoda',
            status: 'checked_in',
            passcode: '789012'
        },
        {
            id: 4,
            channexId: 'channex_004',
            guest: 'Hans Mueller',
            nationality: 'Germany',
            room: '202',
            checkin: '2026-01-10',
            checkout: '2026-01-14',
            ota: 'trip',
            status: 'confirmed',
            passcode: null
        },
        {
            id: 5,
            channexId: 'channex_005',
            guest: 'Kim Min-jun',
            nationality: 'South Korea',
            room: '301',
            checkin: '2026-01-07',
            checkout: '2026-01-09',
            ota: 'airbnb',
            status: 'checked_in',
            passcode: '456789'
        }
    ],

    rooms: [
        { id: 1, number: '101', name: 'Studio A', type: 'studio', status: 'available', lockId: 10001 },
        { id: 2, number: '102', name: 'Studio B', type: 'studio', status: 'occupied', lockId: 10002 },
        { id: 3, number: '201', name: '1BR Suite', type: '1br', status: 'occupied', lockId: 10003 },
        { id: 4, number: '202', name: '1BR Deluxe', type: '1br', status: 'cleaning', lockId: 10004 },
        { id: 5, number: '301', name: '2BR Family', type: '2br', status: 'occupied', lockId: 10005 },
        { id: 6, number: '302', name: '2BR Premium', type: '2br', status: 'maintenance', lockId: 10006 }
    ],

    locks: [
        { id: 10001, name: 'Room 101 - Studio A', battery: 85, online: true },
        { id: 10002, name: 'Room 102 - Studio B', battery: 90, online: true },
        { id: 10003, name: 'Room 201 - 1BR Suite', battery: 75, online: true },
        { id: 10004, name: 'Room 202 - 1BR Deluxe', battery: 60, online: false },
        { id: 10005, name: 'Room 301 - 2BR Family', battery: 95, online: true },
        { id: 10006, name: 'Room 302 - 2BR Premium', battery: 30, online: false }
    ],

    guests: [
        { id: 1, name: 'John Smith', nationality: 'United States', passport: 'US12345678', bookingId: 1, xncExported: false },
        { id: 2, name: 'Marie Dupont', nationality: 'France', passport: 'FR87654321', bookingId: 2, xncExported: false },
        { id: 3, name: 'Tanaka Yuki', nationality: 'Japan', passport: 'JP11223344', bookingId: 3, xncExported: true },
        { id: 4, name: 'Hans Mueller', nationality: 'Germany', passport: 'DE99887766', bookingId: 4, xncExported: false },
        { id: 5, name: 'Kim Min-jun', nationality: 'South Korea', passport: 'KR55667788', bookingId: 5, xncExported: false }
    ],

    housekeepingTasks: [
        { id: 1, room: '202', type: 'checkout_clean', assignee: 'Maria', priority: 'high', status: 'in_progress', createdAt: new Date() },
        { id: 2, room: '101', type: 'turndown', assignee: 'John', priority: 'normal', status: 'pending', createdAt: new Date() },
        { id: 3, room: '301', type: 'deep_clean', assignee: 'Maria', priority: 'low', status: 'pending', createdAt: new Date() }
    ],

    maintenanceIssues: [
        { id: 1, room: '302', issue: 'AC not cooling', severity: 'high', reportedAt: new Date(), status: 'open', reporter: 'Guest' },
        { id: 2, room: '201', issue: 'Leaky faucet', severity: 'medium', reportedAt: new Date(Date.now() - 86400000), status: 'in_progress', reporter: 'Housekeeping' }
    ],

    staff: [
        { id: 1, name: 'Maria', role: 'housekeeping', available: true },
        { id: 2, name: 'John', role: 'housekeeping', available: true },
        { id: 3, name: 'Pedro', role: 'maintenance', available: false }
    ]
};

// ============================================
// Data Fetchers (API with Mock fallback)
// ============================================

async function fetchStats() {
    if (!USE_MOCK_DATA) {
        try {
            return await apiRequest('/crud/stats');
        } catch (e) { }
    }
    return mockData.stats;
}

async function fetchBookings(filters = {}) {
    if (!USE_MOCK_DATA) {
        try {
            let query = '';
            if (filters.status) query += `&status=${filters.status}`;
            if (filters.ota) query += `&ota=${filters.ota}`;
            return await apiRequest(`/crud/bookings?${query.substring(1)}`);
        } catch (e) { }
    }

    let data = [...mockData.bookings];
    if (filters.status) data = data.filter(b => b.status === filters.status);
    if (filters.ota) data = data.filter(b => b.ota === filters.ota);
    return data;
}

async function fetchTodayBookings() {
    if (!USE_MOCK_DATA) {
        try {
            return await apiRequest('/crud/bookings/today');
        } catch (e) { }
    }

    const today = new Date().toISOString().split('T')[0];
    return mockData.bookings.filter(b =>
        b.checkin === today || b.checkout === today || b.status === 'checked_in'
    );
}

async function fetchRooms() {
    if (!USE_MOCK_DATA) {
        try {
            return await apiRequest('/crud/rooms');
        } catch (e) { }
    }
    return mockData.rooms;
}

async function fetchLocks() {
    if (!USE_MOCK_DATA) {
        try {
            return await apiRequest('/crud/locks');
        } catch (e) { }
    }
    return mockData.locks;
}

async function fetchGuests() {
    if (!USE_MOCK_DATA) {
        try {
            return await apiRequest('/crud/guests');
        } catch (e) { }
    }
    return mockData.guests;
}

async function fetchPendingXNCGuests() {
    if (!USE_MOCK_DATA) {
        try {
            return await apiRequest('/crud/guests/pending-xnc');
        } catch (e) { }
    }
    return mockData.guests.filter(g => !g.xncExported);
}

// ============================================
// DOM Ready
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    initCurrentDate();
    initEventListeners();

    // Check API connection
    await checkApiConnection();

    // Load dashboard
    loadDashboard();
});

// ============================================
// Navigation
// ============================================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            showPage(page);

            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            document.getElementById('page-title').textContent =
                page.charAt(0).toUpperCase() + page.slice(1);
        });
    });
}

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => p.classList.remove('active'));

    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');

        switch (pageName) {
            case 'dashboard': loadDashboard(); break;
            case 'bookings': loadBookings(); break;
            case 'rooms': loadRooms(); break;
            case 'guests': loadGuests(); break;
            case 'reports': loadReports(); break;
            case 'locks': loadLocks(); break;
            case 'housekeeping': loadHousekeeping(); break;
        }
    }
}

function initCurrentDate() {
    const dateEl = document.getElementById('current-date');
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
    });

    const reportDate = document.getElementById('report-date');
    if (reportDate) {
        reportDate.value = now.toISOString().split('T')[0];
    }
}

// ============================================
// Dashboard
// ============================================

async function loadDashboard() {
    // Fetch stats
    const stats = await fetchStats();

    document.getElementById('total-bookings').textContent = stats.totalBookings;
    document.getElementById('today-checkins').textContent = stats.todayCheckins;
    document.getElementById('today-checkouts').textContent = stats.todayCheckouts;
    document.getElementById('occupancy-rate').textContent = stats.occupancyRate + '%';

    // Fetch today's bookings
    const todayBookings = await fetchTodayBookings();
    const tbody = document.getElementById('today-bookings');

    tbody.innerHTML = todayBookings.map(b => `
        <tr>
            <td>
                <div style="font-weight: 500">${b.guest}</div>
                <div style="font-size: 12px; color: var(--text-muted)">${b.nationality}</div>
            </td>
            <td>${b.room}</td>
            <td><span class="ota-badge ${b.ota}">${formatOta(b.ota)}</span></td>
            <td><span class="status-badge ${b.status}">${formatStatus(b.status)}</span></td>
            <td>
                ${b.passcode
            ? `<code style="background: var(--bg-hover); padding: 4px 8px; border-radius: 4px">${b.passcode}</code>`
            : '<span style="color: var(--text-muted)">Not Generated</span>'
        }
            </td>
            <td>
                <button class="btn btn-outline" onclick="viewBooking(${b.id})" style="padding: 6px 12px; font-size: 12px">View</button>
                ${!b.passcode ? `<button class="btn btn-success" onclick="generatePasscode(${b.id})" style="padding: 6px 12px; font-size: 12px">🔑 Generate</button>` : ''}
            </td>
        </tr>
    `).join('');
}

// ============================================
// Bookings
// ============================================

async function loadBookings() {
    const status = document.getElementById('filter-status')?.value;
    const ota = document.getElementById('filter-ota')?.value;

    const bookings = await fetchBookings({ status, ota });
    const tbody = document.getElementById('all-bookings');

    tbody.innerHTML = bookings.map(b => `
        <tr>
            <td><code>${b.channexId || 'BK' + b.id}</code></td>
            <td>
                <div style="font-weight: 500">${b.guest}</div>
                <div style="font-size: 12px; color: var(--text-muted)">${b.nationality}</div>
            </td>
            <td>${b.room}</td>
            <td>${formatDate(b.checkin)}</td>
            <td>${formatDate(b.checkout)}</td>
            <td><span class="ota-badge ${b.ota}">${formatOta(b.ota)}</span></td>
            <td><span class="status-badge ${b.status}">${formatStatus(b.status)}</span></td>
            <td>
                <button class="btn btn-outline" onclick="viewBooking(${b.id})" style="padding: 6px 12px; font-size: 12px">View</button>
            </td>
        </tr>
    `).join('');
}

// ============================================
// Rooms
// ============================================

async function loadRooms() {
    const rooms = await fetchRooms();
    const grid = document.getElementById('rooms-grid');

    grid.innerHTML = rooms.map(r => `
        <div class="room-card" onclick="showRoomActions(${r.id}, '${r.number}', '${r.status}')">
            <div class="room-number">${r.number}</div>
            <div class="room-type">${r.name || r.type}</div>
            <span class="room-status ${r.status}">${formatStatus(r.status)}</span>
        </div>
    `).join('');
}

function showRoomActions(roomId, roomNumber, currentStatus) {
    const statusOptions = ['available', 'occupied', 'cleaning', 'maintenance'];

    openModal(`Room ${roomNumber}`, `
        <div style="display: grid; gap: 16px;">
            <div><strong>Current Status:</strong> <span class="status-badge ${currentStatus}">${formatStatus(currentStatus)}</span></div>
            <hr>
            <div><strong>Change Status:</strong></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                ${statusOptions.map(s => `
                    <button class="btn ${s === currentStatus ? 'btn-primary' : 'btn-outline'}" 
                            onclick="updateRoomStatus(${roomId}, '${s}')" 
                            ${s === currentStatus ? 'disabled' : ''}>
                        ${formatStatus(s)}
                    </button>
                `).join('')}
            </div>
        </div>
    `);
}

async function updateRoomStatus(roomId, status) {
    showToast('Updating room status...', 'info');

    if (!USE_MOCK_DATA) {
        try {
            await apiRequest(`/crud/rooms/${roomId}/status?status=${status}`, { method: 'PUT' });
        } catch (e) { }
    }

    // Update mock data
    const room = mockData.rooms.find(r => r.id === roomId);
    if (room) room.status = status;

    closeModal();
    loadRooms();
    showToast(`Room status updated to ${formatStatus(status)}`, 'success');
}

// ============================================
// Locks
// ============================================

async function loadLocks() {
    const locks = await fetchLocks();
    const grid = document.getElementById('locks-grid');

    grid.innerHTML = locks.map(l => `
        <div class="lock-card">
            <div class="lock-icon">${l.online ? '🔓' : '🔴'}</div>
            <div class="lock-name">${l.name}</div>
            <div class="lock-battery">
                🔋 ${l.battery}% ${l.battery < 20 ? '⚠️' : ''}
            </div>
            <div style="font-size: 12px; color: ${l.online ? '#10b981' : '#ef4444'}; margin-top: 8px">
                ${l.online ? '● Online' : '● Offline'}
            </div>
            <div class="lock-actions">
                <button class="lock-btn" onclick="unlockDoor(${l.id})" ${!l.online ? 'disabled' : ''}>🔓 Unlock</button>
                <button class="lock-btn" onclick="viewPasscodes(${l.id})">🔑 Codes</button>
            </div>
        </div>
    `).join('');
}

// ============================================
// Guests
// ============================================

async function loadGuests() {
    const guests = await fetchGuests();
    const tbody = document.getElementById('all-guests');

    tbody.innerHTML = guests.map(g => `
        <tr>
            <td><strong>${g.name}</strong></td>
            <td>${g.nationality}</td>
            <td><code>${g.passport}</code></td>
            <td>BK${g.bookingId || g.id}</td>
            <td>
                <span class="status-badge ${g.xncExported ? 'checked_out' : 'pending'}">
                    ${g.xncExported ? '✓ Exported' : '⏳ Pending'}
                </span>
            </td>
            <td>
                <button class="btn btn-outline" onclick="viewGuest(${g.id})" style="padding: 6px 12px; font-size: 12px">View</button>
            </td>
        </tr>
    `).join('');
}

// ============================================
// Reports
// ============================================

async function loadReports() {
    const pendingGuests = await fetchPendingXNCGuests();
    const tbody = document.getElementById('pending-guests');

    tbody.innerHTML = pendingGuests.map(g => `
        <tr>
            <td><input type="checkbox" class="guest-checkbox" data-id="${g.id}"></td>
            <td><strong>${g.name}</strong></td>
            <td>${g.nationality}</td>
            <td><code>${g.passport}</code></td>
            <td>${g.checkin || 'N/A'}</td>
            <td><span class="status-badge pending">Pending</span></td>
        </tr>
    `).join('');

    document.getElementById('select-all-guests')?.addEventListener('change', (e) => {
        document.querySelectorAll('.guest-checkbox').forEach(cb => {
            cb.checked = e.target.checked;
        });
    });
}

// ============================================
// Actions
// ============================================

async function generatePasscode(bookingId) {
    showToast('Generating passcode...', 'info');

    if (!USE_MOCK_DATA) {
        try {
            const result = await apiRequest(`/crud/bookings/${bookingId}/generate-passcode`, { method: 'POST' });
            showToast(`Passcode ${result.passcode} generated!`, 'success');
            loadDashboard();
            return;
        } catch (e) { }
    }

    // Mock fallback
    setTimeout(() => {
        const booking = mockData.bookings.find(b => b.id === bookingId);
        if (booking) {
            booking.passcode = String(Math.floor(100000 + Math.random() * 900000));
            showToast(`Passcode ${booking.passcode} generated!`, 'success');
            loadDashboard();
        }
    }, 1000);
}

function sendPasscodes() {
    showToast('Sending passcodes to all guests...', 'info');
    setTimeout(() => showToast('Passcodes sent successfully!', 'success'), 1500);
}

async function generateXNCReport() {
    const reportDate = document.getElementById('report-date')?.value || new Date().toISOString().split('T')[0];
    const format = document.querySelector('input[name="report-format"]:checked')?.value || 'csv';

    showToast(`Generating ${format.toUpperCase()} report...`, 'info');

    if (!USE_MOCK_DATA) {
        try {
            const result = await apiRequest(`/reports/xnc/generate?report_date=${reportDate}&format=${format}`, { method: 'POST' });
            showToast(`Report generated: ${result.file_path}`, 'success');
            return;
        } catch (e) { }
    }

    setTimeout(() => showToast(`XNC Report generated successfully!`, 'success'), 2000);
}

async function syncBookings() {
    showToast('Syncing with Channex...', 'info');

    // Reload data
    await checkApiConnection();
    loadDashboard();

    setTimeout(() => showToast('Sync complete!', 'success'), 2000);
}

function unlockDoor(lockId) {
    const lock = mockData.locks.find(l => l.id === lockId);
    showToast(`Unlocking ${lock?.name}...`, 'info');
    setTimeout(() => showToast(`${lock?.name} unlocked!`, 'success'), 1500);
}

async function viewBooking(bookingId) {
    let booking;

    if (!USE_MOCK_DATA) {
        try {
            booking = await apiRequest(`/crud/bookings/${bookingId}`);
        } catch (e) { }
    }

    if (!booking) {
        booking = mockData.bookings.find(b => b.id === bookingId);
    }

    if (booking) {
        openModal('Booking Details', `
            <div style="display: grid; gap: 16px;">
                <div><strong>Booking ID:</strong> ${booking.channexId || 'BK' + booking.id}</div>
                <div><strong>Guest:</strong> ${booking.guest?.name || booking.guest}</div>
                <div><strong>Nationality:</strong> ${booking.guest?.nationality || booking.nationality}</div>
                <div><strong>Room:</strong> ${booking.room}</div>
                <div><strong>Check-in:</strong> ${formatDate(booking.checkin)}</div>
                <div><strong>Check-out:</strong> ${formatDate(booking.checkout)}</div>
                <div><strong>OTA:</strong> ${formatOta(booking.ota)}</div>
                <div><strong>Status:</strong> <span class="status-badge ${booking.status}">${formatStatus(booking.status)}</span></div>
                <div><strong>Passcode:</strong> ${booking.passcode || 'Not generated'}</div>
                ${booking.backupPasscode ? `<div><strong>Backup:</strong> ${booking.backupPasscode}</div>` : ''}
                <hr>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    ${!booking.passcode ? `<button class="btn btn-success" onclick="generatePasscode(${booking.id}); closeModal();">🔑 Generate Passcode</button>` : ''}
                    <button class="btn btn-primary" onclick="showToast('Passcode sent to guest!', 'success'); closeModal();">📨 Send to Guest</button>
                    ${booking.status === 'confirmed' ? `<button class="btn btn-outline" onclick="updateBookingStatus(${booking.id}, 'checked_in')">Check In</button>` : ''}
                    ${booking.status === 'checked_in' ? `<button class="btn btn-outline" onclick="updateBookingStatus(${booking.id}, 'checked_out')">Check Out</button>` : ''}
                </div>
            </div>
        `);
    }
}

async function updateBookingStatus(bookingId, status) {
    showToast('Updating booking status...', 'info');

    if (!USE_MOCK_DATA) {
        try {
            await apiRequest(`/crud/bookings/${bookingId}/status?status=${status}`, { method: 'PUT' });
        } catch (e) { }
    }

    // Update mock data
    const booking = mockData.bookings.find(b => b.id === bookingId);
    if (booking) {
        booking.status = status;
        const room = mockData.rooms.find(r => r.number === booking.room);
        if (room) {
            room.status = status === 'checked_in' ? 'occupied' : 'cleaning';
        }
    }

    closeModal();
    loadDashboard();
    showToast(`Booking ${formatStatus(status)}`, 'success');
}

function viewPasscodes(lockId) {
    const lock = mockData.locks.find(l => l.id === lockId);
    const roomBookings = mockData.bookings.filter(b => {
        const room = mockData.rooms.find(r => r.lockId === lockId);
        return room && b.room === room.number && b.passcode;
    });

    openModal(`Passcodes - ${lock?.name}`, `
        <table class="data-table">
            <thead>
                <tr><th>Code</th><th>Guest</th><th>Status</th></tr>
            </thead>
            <tbody>
                ${roomBookings.length > 0 ? roomBookings.map(b => `
                    <tr>
                        <td><code>${b.passcode}</code></td>
                        <td>${b.guest}</td>
                        <td><span class="status-badge ${b.status}">${formatStatus(b.status)}</span></td>
                    </tr>
                `).join('') : '<tr><td colspan="3" style="text-align: center; color: var(--text-muted)">No active passcodes</td></tr>'}
            </tbody>
        </table>
    `);
}

function viewLocks() {
    showPage('locks');
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelector('[data-page="locks"]').classList.add('active');
    document.getElementById('page-title').textContent = 'Smart Locks';
}

// ============================================
// Helpers
// ============================================

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatStatus(status) {
    const map = {
        confirmed: 'Confirmed', checked_in: 'Checked In', checked_out: 'Checked Out',
        cancelled: 'Cancelled', pending: 'Pending', available: 'Available',
        occupied: 'Occupied', cleaning: 'Cleaning', maintenance: 'Maintenance'
    };
    return map[status] || status;
}

function formatOta(ota) {
    const map = { airbnb: 'Airbnb', booking: 'Booking.com', agoda: 'Agoda', trip: 'Trip.com' };
    return map[ota] || ota?.charAt(0).toUpperCase() + ota?.slice(1) || 'Direct';
}

// ============================================
// Toast & Modal
// ============================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✓', error: '✗', info: 'ℹ' };
    toast.innerHTML = `<span style="font-size: 18px">${icons[type]}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function openModal(title, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
}

document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target.id === 'modal-overlay') closeModal();
});

// ============================================
// Event Listeners
// ============================================

function initEventListeners() {
    document.getElementById('sync-btn')?.addEventListener('click', syncBookings);

    document.getElementById('new-booking-btn')?.addEventListener('click', () => {
        openModal('New Booking', `
            <form style="display: grid; gap: 16px;">
                <div class="form-group">
                    <label>Guest Name</label>
                    <input type="text" class="form-input" placeholder="Full name" id="new-guest-name">
                </div>
                <div class="form-group">
                    <label>Room</label>
                    <select class="form-input" id="new-room">
                        ${mockData.rooms.filter(r => r.status === 'available').map(r =>
            `<option value="${r.id}">${r.number} - ${r.name}</option>`
        ).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Check-in Date</label>
                    <input type="date" class="form-input" id="new-checkin">
                </div>
                <div class="form-group">
                    <label>Check-out Date</label>
                    <input type="date" class="form-input" id="new-checkout">
                </div>
                <button type="button" class="btn btn-primary" onclick="createBooking()">Create Booking</button>
            </form>
        `);
    });

    document.getElementById('filter-status')?.addEventListener('change', loadBookings);
    document.getElementById('filter-ota')?.addEventListener('change', loadBookings);
}

function createBooking() {
    const guestName = document.getElementById('new-guest-name')?.value;
    if (!guestName) {
        showToast('Please fill in guest name', 'error');
        return;
    }
    showToast('Booking created successfully!', 'success');
    closeModal();
    loadDashboard();
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// ============================================
// Passport OCR
// ============================================

function showPassportScanModal() {
    openModal('🛂 Passport Scanner', `
        <div style="display: grid; gap: 20px;">
            <!-- Tabs -->
            <div style="display: flex; gap: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px;">
                <button class="btn btn-primary" onclick="showUploadTab()" id="tab-upload">📷 Upload Image</button>
                <button class="btn btn-outline" onclick="showMRZTab()" id="tab-mrz">⌨️ Enter MRZ</button>
                <button class="btn btn-outline" onclick="showDemoTab()" id="tab-demo">🧪 Demo</button>
            </div>
            
            <!-- Upload Tab -->
            <div id="passport-upload-tab">
                <div class="form-group">
                    <label>Select Booking</label>
                    <select id="passport-booking-id" class="form-input">
                        ${mockData.bookings.map(b =>
        `<option value="${b.id}">${b.guest} - Room ${b.room}</option>`
    ).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Passport Image</label>
                    <div style="border: 2px dashed var(--border-color); border-radius: 8px; padding: 40px; text-align: center; cursor: pointer;" 
                         onclick="document.getElementById('passport-file').click()"
                         id="drop-zone">
                        <div style="font-size: 48px; margin-bottom: 12px;">📷</div>
                        <div>Click to upload or drag & drop</div>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">JPEG, PNG, or WEBP (max 10MB)</div>
                        <input type="file" id="passport-file" accept="image/*" style="display: none;" onchange="handlePassportFile(this)">
                    </div>
                    <div id="file-preview" style="margin-top: 12px; display: none;">
                        <img id="passport-preview" style="max-width: 100%; max-height: 200px; border-radius: 8px;">
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="uploadPassport()" style="width: 100%;">
                    🔍 Scan & Extract Data
                </button>
            </div>
            
            <!-- MRZ Manual Tab -->
            <div id="passport-mrz-tab" style="display: none;">
                <div style="background: var(--bg-hover); padding: 12px; border-radius: 8px; margin-bottom: 16px;">
                    <div style="font-size: 12px; color: var(--text-muted);">
                        Enter the 2 MRZ lines from the bottom of the passport (44 characters each)
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Line 1 (starts with P&lt;)</label>
                    <input type="text" id="mrz-line1" class="form-input" style="font-family: monospace; letter-spacing: 1px;"
                           placeholder="P<USASMITH<<JOHN<WILLIAM<<<<<<<<<<<<<<<<<<<<<" maxlength="44">
                </div>
                
                <div class="form-group">
                    <label>Line 2</label>
                    <input type="text" id="mrz-line2" class="form-input" style="font-family: monospace; letter-spacing: 1px;"
                           placeholder="AB12345671USA9001011M3012315<<<<<<<<<<<<<<02" maxlength="44">
                </div>
                
                <button class="btn btn-primary" onclick="parseMRZ()" style="width: 100%;">
                    ✅ Parse MRZ Data
                </button>
            </div>
            
            <!-- Demo Tab -->
            <div id="passport-demo-tab" style="display: none;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 12px; color: white; margin-bottom: 16px;">
                    <h3 style="margin: 0 0 12px 0;">🧪 MRZ Parser Demo</h3>
                    <p style="margin: 0; opacity: 0.9;">Click below to test the MRZ parser with sample data</p>
                </div>
                
                <div style="background: var(--bg-hover); padding: 12px; border-radius: 8px; font-family: monospace; font-size: 12px; margin-bottom: 16px;">
                    <div>P&lt;USASMITH&lt;&lt;JOHN&lt;WILLIAM&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;</div>
                    <div>AB12345671USA9001011M3012315&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;02</div>
                </div>
                
                <button class="btn btn-success" onclick="runPassportDemo()" style="width: 100%;">
                    ▶️ Run Demo
                </button>
            </div>
            
            <!-- Results Area -->
            <div id="passport-results" style="display: none;">
                <hr>
                <h4 style="margin: 0 0 16px 0;">📋 Extracted Data</h4>
                <div id="passport-data-fields"></div>
            </div>
        </div>
    `);
}

function showUploadTab() {
    document.getElementById('passport-upload-tab').style.display = 'block';
    document.getElementById('passport-mrz-tab').style.display = 'none';
    document.getElementById('passport-demo-tab').style.display = 'none';
    document.getElementById('tab-upload').classList.add('btn-primary');
    document.getElementById('tab-upload').classList.remove('btn-outline');
    document.getElementById('tab-mrz').classList.add('btn-outline');
    document.getElementById('tab-mrz').classList.remove('btn-primary');
    document.getElementById('tab-demo').classList.add('btn-outline');
    document.getElementById('tab-demo').classList.remove('btn-primary');
}

function showMRZTab() {
    document.getElementById('passport-upload-tab').style.display = 'none';
    document.getElementById('passport-mrz-tab').style.display = 'block';
    document.getElementById('passport-demo-tab').style.display = 'none';
    document.getElementById('tab-mrz').classList.add('btn-primary');
    document.getElementById('tab-mrz').classList.remove('btn-outline');
    document.getElementById('tab-upload').classList.add('btn-outline');
    document.getElementById('tab-upload').classList.remove('btn-primary');
    document.getElementById('tab-demo').classList.add('btn-outline');
    document.getElementById('tab-demo').classList.remove('btn-primary');
}

function showDemoTab() {
    document.getElementById('passport-upload-tab').style.display = 'none';
    document.getElementById('passport-mrz-tab').style.display = 'none';
    document.getElementById('passport-demo-tab').style.display = 'block';
    document.getElementById('tab-demo').classList.add('btn-primary');
    document.getElementById('tab-demo').classList.remove('btn-outline');
    document.getElementById('tab-upload').classList.add('btn-outline');
    document.getElementById('tab-upload').classList.remove('btn-primary');
    document.getElementById('tab-mrz').classList.add('btn-outline');
    document.getElementById('tab-mrz').classList.remove('btn-primary');
}

let selectedPassportFile = null;

function handlePassportFile(input) {
    const file = input.files[0];
    if (file) {
        selectedPassportFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('passport-preview').src = e.target.result;
            document.getElementById('file-preview').style.display = 'block';
            document.getElementById('drop-zone').innerHTML = `
                <div style="font-size: 24px; margin-bottom: 8px;">✅</div>
                <div>${file.name}</div>
            `;
        };
        reader.readAsDataURL(file);
    }
}

async function uploadPassport() {
    if (!selectedPassportFile) {
        showToast('Please select a passport image', 'error');
        return;
    }

    const bookingId = document.getElementById('passport-booking-id').value;
    showToast('Scanning passport...', 'info');

    if (!USE_MOCK_DATA) {
        try {
            const formData = new FormData();
            formData.append('file', selectedPassportFile);
            formData.append('booking_id', bookingId);

            const response = await fetch(`${API_BASE_URL}/passport/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                displayPassportResult(result);
                showToast('Passport data extracted!', 'success');
            } else {
                showToast(result.message || 'OCR failed. Try manual MRZ entry.', 'error');
            }
            return;
        } catch (e) {
            console.error('Upload error:', e);
        }
    }

    // Mock fallback - simulate OCR
    setTimeout(() => {
        const mockResult = {
            success: true,
            full_name: "JOHN WILLIAM SMITH",
            passport_number: "AB1234567",
            nationality: "United States",
            date_of_birth: "1990-01-15",
            gender: "male",
            expiry_date: "2030-12-31",
            confidence: 0.85,
            message: "Demo: Passport data extracted (mock)"
        };
        displayPassportResult(mockResult);
        showToast('Passport data extracted! (Demo)', 'success');
    }, 1500);
}

async function parseMRZ() {
    const line1 = document.getElementById('mrz-line1').value.toUpperCase();
    const line2 = document.getElementById('mrz-line2').value.toUpperCase();

    if (line1.length < 30 || line2.length < 30) {
        showToast('Please enter valid MRZ lines (at least 30 characters each)', 'error');
        return;
    }

    showToast('Parsing MRZ...', 'info');

    if (!USE_MOCK_DATA) {
        try {
            const result = await apiRequest('/passport/parse-mrz', {
                method: 'POST',
                body: JSON.stringify({ mrz_line1: line1, mrz_line2: line2 })
            });

            if (result.success) {
                displayPassportResult(result);
                showToast('MRZ parsed successfully!', 'success');
            } else {
                showToast(result.message || 'Failed to parse MRZ', 'error');
            }
            return;
        } catch (e) {
            console.error('Parse error:', e);
        }
    }

    // Local MRZ parsing (simplified)
    const parsed = parseLocalMRZ(line1, line2);
    if (parsed) {
        displayPassportResult(parsed);
        showToast('MRZ parsed successfully!', 'success');
    } else {
        showToast('Failed to parse MRZ. Check format.', 'error');
    }
}

function parseLocalMRZ(line1, line2) {
    try {
        // Parse Line 1: P<COUNTRY<SURNAME<<GIVEN_NAMES
        const namePart = line1.substring(5).replace(/</g, ' ').trim();
        const nameParts = namePart.split('  ');
        const surname = nameParts[0]?.trim() || '';
        const givenNames = nameParts.slice(1).join(' ').trim() || '';

        // Parse Line 2
        const passportNumber = line2.substring(0, 9).replace(/</g, '');
        const nationality = line2.substring(10, 13);
        const dobStr = line2.substring(13, 19);
        const gender = line2.substring(20, 21);
        const expiryStr = line2.substring(21, 27);

        // Parse dates (YYMMDD)
        const parseMRZDate = (str) => {
            const yy = parseInt(str.substring(0, 2));
            const mm = str.substring(2, 4);
            const dd = str.substring(4, 6);
            const year = yy > 30 ? 1900 + yy : 2000 + yy;
            return `${year}-${mm}-${dd}`;
        };

        const countries = {
            'USA': 'United States', 'GBR': 'United Kingdom', 'FRA': 'France',
            'DEU': 'Germany', 'JPN': 'Japan', 'KOR': 'South Korea',
            'CHN': 'China', 'VNM': 'Vietnam', 'AUS': 'Australia'
        };

        return {
            success: true,
            full_name: `${givenNames} ${surname}`.trim(),
            surname: surname,
            given_names: givenNames,
            passport_number: passportNumber,
            nationality: countries[nationality] || nationality,
            date_of_birth: parseMRZDate(dobStr),
            gender: gender === 'M' ? 'male' : (gender === 'F' ? 'female' : 'unknown'),
            expiry_date: parseMRZDate(expiryStr),
            confidence: 0.95
        };
    } catch (e) {
        console.error('Local MRZ parse error:', e);
        return null;
    }
}

async function runPassportDemo() {
    showToast('Running demo...', 'info');

    if (!USE_MOCK_DATA) {
        try {
            const result = await apiRequest('/passport/demo');
            displayPassportResult(result.output);
            showToast('Demo complete!', 'success');
            return;
        } catch (e) { }
    }

    // Local demo
    setTimeout(() => {
        const demoResult = parseLocalMRZ(
            'P<USASMITH<<JOHN<WILLIAM<<<<<<<<<<<<<<<<<<<<<',
            'AB12345671USA9001011M3012315<<<<<<<<<<<<<<02'
        );
        displayPassportResult(demoResult);
        showToast('Demo complete!', 'success');
    }, 500);
}

function displayPassportResult(data) {
    const resultsDiv = document.getElementById('passport-results');
    const fieldsDiv = document.getElementById('passport-data-fields');

    resultsDiv.style.display = 'block';

    const fields = [
        { label: 'Full Name', value: data.full_name, icon: '👤' },
        { label: 'Passport Number', value: data.passport_number, icon: '🛂' },
        { label: 'Nationality', value: data.nationality, icon: '🌍' },
        { label: 'Date of Birth', value: data.date_of_birth, icon: '🎂' },
        { label: 'Gender', value: data.gender, icon: '⚧' },
        { label: 'Expiry Date', value: data.expiry_date, icon: '📅' },
        { label: 'Confidence', value: data.confidence ? `${(data.confidence * 100).toFixed(0)}%` : 'N/A', icon: '📊' }
    ];

    fieldsDiv.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            ${fields.map(f => `
                <div style="background: var(--bg-hover); padding: 12px; border-radius: 8px;">
                    <div style="font-size: 12px; color: var(--text-muted);">${f.icon} ${f.label}</div>
                    <div style="font-weight: 600; margin-top: 4px;">${f.value || 'N/A'}</div>
                </div>
            `).join('')}
        </div>
        <button class="btn btn-success" onclick="applyPassportData()" style="width: 100%;">
            ✅ Apply to Guest Record
        </button>
    `;

    // Store the result for later use
    window.lastPassportData = data;
}

async function applyPassportData() {
    const data = window.lastPassportData;
    if (!data) {
        showToast('No passport data to apply', 'error');
        return;
    }

    const bookingId = document.getElementById('passport-booking-id')?.value;
    showToast('Applying passport data...', 'info');

    if (!USE_MOCK_DATA && bookingId) {
        try {
            await apiRequest(`/passport/apply-to-guest/${bookingId}`, {
                method: 'POST',
                body: JSON.stringify(data)
            });
        } catch (e) { }
    }

    // Update mock data
    const guest = mockData.guests.find(g => g.bookingId == bookingId || g.id == bookingId);
    if (guest) {
        guest.name = data.full_name;
        guest.nationality = data.nationality;
        guest.passport = data.passport_number;
    }

    closeModal();
    loadGuests();
    showToast('Guest record updated with passport data!', 'success');
}

function viewGuest(guestId) {
    const guest = mockData.guests.find(g => g.id === guestId);
    if (!guest) return;

    openModal('Guest Details', `
        <div style="display: grid; gap: 16px;">
            <div><strong>Name:</strong> ${guest.name}</div>
            <div><strong>Nationality:</strong> ${guest.nationality}</div>
            <div><strong>Passport:</strong> <code>${guest.passport}</code></div>
            <div><strong>XNC Status:</strong> 
                <span class="status-badge ${guest.xncExported ? 'checked_out' : 'pending'}">
                    ${guest.xncExported ? '✓ Exported' : '⏳ Pending'}
                </span>
            </div>
            <hr>
            <div style="display: flex; gap: 12px;">
                <button class="btn btn-primary" onclick="showPassportScanModal()">🛂 Scan Passport</button>
                ${!guest.xncExported ? `<button class="btn btn-outline" onclick="markGuestExported(${guest.id})">📋 Mark Exported</button>` : ''}
            </div>
        </div>
    `);
}

function markGuestExported(guestId) {
    const guest = mockData.guests.find(g => g.id === guestId);
    if (guest) guest.xncExported = true;
    closeModal();
    loadGuests();
    showToast('Guest marked as exported to XNC', 'success');
}

// ============================================
// Housekeeping & Maintenance
// ============================================

function loadHousekeeping() {
    loadHousekeepingGrid();
    loadHousekeepingTasks();
    loadMaintenanceIssues();
}

async function loadHousekeepingGrid() {
    const grid = document.getElementById('housekeeping-grid');
    if (!grid) return;

    let rooms = mockData.rooms;

    // Try to fetch from API
    if (!USE_MOCK_DATA) {
        try {
            rooms = await apiRequest('/housekeeping/rooms');
            // Map API response to expected format
            rooms = rooms.map(r => ({
                id: r.id,
                number: r.room_number,
                name: r.room_name,
                status: r.status
            }));
        } catch (e) {
            console.log('Using mock data for housekeeping grid');
        }
    }

    const cleaningStatuses = {
        'available': { icon: '✅', label: 'Clean/Ready', color: '#10b981' },
        'occupied': { icon: '🛏️', label: 'Occupied', color: '#6366f1' },
        'cleaning': { icon: '🧹', label: 'Cleaning', color: '#f59e0b' },
        'maintenance': { icon: '🔧', label: 'Maintenance', color: '#ef4444' }
    };

    grid.innerHTML = rooms.map(r => {
        const status = cleaningStatuses[r.status] || cleaningStatuses['available'];
        return `
            <div class="room-card" onclick="showHousekeepingActions('${r.id}', '${r.number}', '${r.status}')"
                 style="border-left: 4px solid ${status.color};">
                <div class="room-number">${r.number}</div>
                <div style="font-size: 24px; margin: 8px 0;">${status.icon}</div>
                <span class="room-status ${r.status}">${status.label}</span>
            </div>
        `;
    }).join('');
}

function loadHousekeepingTasks() {
    const tasks = mockData.housekeepingTasks;
    const tbody = document.getElementById('housekeeping-tasks');
    if (!tbody) return;

    const taskTypes = {
        'checkout_clean': 'Checkout Clean',
        'turndown': 'Turndown Service',
        'deep_clean': 'Deep Clean',
        'refresh': 'Refresh'
    };

    tbody.innerHTML = tasks.map(t => `
        <tr>
            <td><strong>${t.room}</strong></td>
            <td>${taskTypes[t.type] || t.type}</td>
            <td>${t.assignee}</td>
            <td><span class="status-badge ${t.priority === 'high' ? 'cancelled' : t.priority === 'normal' ? 'confirmed' : 'pending'}">${t.priority}</span></td>
            <td><span class="status-badge ${t.status === 'in_progress' ? 'checked_in' : 'pending'}">${formatStatus(t.status)}</span></td>
            <td>
                <button class="btn btn-outline" onclick="completeTask(${t.id})" style="padding: 6px 12px; font-size: 12px;">
                    ✓ Complete
                </button>
            </td>
        </tr>
    `).join('');
}

function loadMaintenanceIssues() {
    const issues = mockData.maintenanceIssues;
    const tbody = document.getElementById('maintenance-issues');
    if (!tbody) return;

    tbody.innerHTML = issues.map(i => `
        <tr>
            <td><strong>${i.room}</strong></td>
            <td>${i.issue}</td>
            <td><span class="status-badge ${i.severity === 'high' ? 'cancelled' : i.severity === 'medium' ? 'pending' : 'confirmed'}">${i.severity}</span></td>
            <td>${new Date(i.reportedAt).toLocaleDateString()}</td>
            <td><span class="status-badge ${i.status === 'open' ? 'cancelled' : 'checked_in'}">${i.status}</span></td>
            <td>
                <button class="btn btn-outline" onclick="resolveIssue(${i.id})" style="padding: 6px 12px; font-size: 12px;">
                    🔧 Resolve
                </button>
            </td>
        </tr>
    `).join('');
}

function showHousekeepingActions(roomId, roomNumber, currentStatus) {
    const statuses = ['available', 'cleaning', 'maintenance'];

    openModal(`Room ${roomNumber} - Housekeeping`, `
        <div style="display: grid; gap: 16px;">
            <div><strong>Current Status:</strong> <span class="status-badge ${currentStatus}">${formatStatus(currentStatus)}</span></div>
            <hr>
            <div><strong>Mark as:</strong></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                ${statuses.map(s => `
                    <button class="btn ${s === currentStatus ? 'btn-primary' : 'btn-outline'}" 
                            onclick="updateRoomStatus(${roomId}, '${s}')"
                            ${s === currentStatus ? 'disabled' : ''}>
                        ${formatStatus(s)}
                    </button>
                `).join('')}
            </div>
            <hr>
            <button class="btn btn-outline" onclick="showReportIssueModal('${roomNumber}')">
                🔧 Report Maintenance Issue
            </button>
        </div>
    `);
}

function showTaskAssignModal() {
    const rooms = mockData.rooms.filter(r => r.status !== 'cleaning');
    const staff = mockData.staff.filter(s => s.role === 'housekeeping' && s.available);

    openModal('➕ Assign Cleaning Task', `
        <form style="display: grid; gap: 16px;">
            <div class="form-group">
                <label>Room</label>
                <select id="task-room" class="form-input">
                    ${rooms.map(r => `<option value="${r.number}">${r.number} - ${r.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Task Type</label>
                <select id="task-type" class="form-input">
                    <option value="checkout_clean">Checkout Clean</option>
                    <option value="turndown">Turndown Service</option>
                    <option value="deep_clean">Deep Clean</option>
                    <option value="refresh">Quick Refresh</option>
                </select>
            </div>
            <div class="form-group">
                <label>Assign To</label>
                <select id="task-assignee" class="form-input">
                    ${staff.map(s => `<option value="${s.name}">${s.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Priority</label>
                <select id="task-priority" class="form-input">
                    <option value="normal">Normal</option>
                    <option value="high">High (Urgent)</option>
                    <option value="low">Low</option>
                </select>
            </div>
            <button type="button" class="btn btn-primary" onclick="createHousekeepingTask()">
                ✓ Assign Task
            </button>
        </form>
    `);
}

function createHousekeepingTask() {
    const room = document.getElementById('task-room').value;
    const type = document.getElementById('task-type').value;
    const assignee = document.getElementById('task-assignee').value;
    const priority = document.getElementById('task-priority').value;

    const newTask = {
        id: mockData.housekeepingTasks.length + 1,
        room, type, assignee, priority,
        status: 'pending',
        createdAt: new Date()
    };

    mockData.housekeepingTasks.push(newTask);
    closeModal();
    loadHousekeeping();
    showToast(`Task assigned to ${assignee}`, 'success');

    // WebSocket would broadcast this
    broadcastUpdate('housekeeping_task_created', newTask);
}

function completeTask(taskId) {
    const task = mockData.housekeepingTasks.find(t => t.id === taskId);
    if (task) {
        task.status = 'completed';
        // Update room status
        const room = mockData.rooms.find(r => r.number === task.room);
        if (room) room.status = 'available';
    }
    loadHousekeeping();
    showToast('Task marked as complete!', 'success');
    broadcastUpdate('housekeeping_task_completed', { taskId });
}

function showReportIssueModal(roomNumber = '') {
    const rooms = mockData.rooms;

    openModal('🔧 Report Maintenance Issue', `
        <form style="display: grid; gap: 16px;">
            <div class="form-group">
                <label>Room</label>
                <select id="issue-room" class="form-input">
                    ${rooms.map(r => `<option value="${r.number}" ${r.number === roomNumber ? 'selected' : ''}>${r.number} - ${r.name}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Issue Description</label>
                <input type="text" id="issue-desc" class="form-input" placeholder="e.g., AC not working">
            </div>
            <div class="form-group">
                <label>Severity</label>
                <select id="issue-severity" class="form-input">
                    <option value="low">Low - Minor inconvenience</option>
                    <option value="medium">Medium - Should fix soon</option>
                    <option value="high">High - Urgent/Safety issue</option>
                </select>
            </div>
            <button type="button" class="btn btn-primary" onclick="reportMaintenanceIssue()">
                📝 Submit Issue
            </button>
        </form>
    `);
}

function reportMaintenanceIssue() {
    const room = document.getElementById('issue-room').value;
    const issue = document.getElementById('issue-desc').value;
    const severity = document.getElementById('issue-severity').value;

    if (!issue) {
        showToast('Please describe the issue', 'error');
        return;
    }

    const newIssue = {
        id: mockData.maintenanceIssues.length + 1,
        room, issue, severity,
        reportedAt: new Date(),
        status: 'open',
        reporter: 'Staff'
    };

    mockData.maintenanceIssues.push(newIssue);

    // Update room status if high severity
    if (severity === 'high') {
        const roomObj = mockData.rooms.find(r => r.number === room);
        if (roomObj) roomObj.status = 'maintenance';
    }

    closeModal();
    loadHousekeeping();
    showToast('Maintenance issue reported!', 'success');
    broadcastUpdate('maintenance_issue_reported', newIssue);
}

function resolveIssue(issueId) {
    const issue = mockData.maintenanceIssues.find(i => i.id === issueId);
    if (issue) {
        issue.status = 'resolved';
        // If room was in maintenance, set to available
        const room = mockData.rooms.find(r => r.number === issue.room);
        if (room && room.status === 'maintenance') {
            room.status = 'available';
        }
    }
    loadHousekeeping();
    showToast('Issue resolved!', 'success');
}

// ============================================
// Mobile Navigation
// ============================================

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
}

function closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
}

function mobileNav(pageName) {
    showPage(pageName);

    // Update mobile nav active state
    document.querySelectorAll('.mobile-nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });

    // Update page title
    document.getElementById('page-title').textContent =
        pageName.charAt(0).toUpperCase() + pageName.slice(1);

    // Also update sidebar nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });
}

// ============================================
// WebSocket (Real-time Updates)
// ============================================

let websocket = null;

function initWebSocket() {
    // WebSocket connection (would connect to backend)
    const wsUrl = 'ws://localhost:8000/ws';

    try {
        // For now, we simulate WebSocket with polling
        console.log('🔌 WebSocket initialized (simulation mode)');

        // Simulate receiving updates every 30 seconds
        setInterval(() => {
            if (!USE_MOCK_DATA) {
                checkForUpdates();
            }
        }, 30000);

    } catch (e) {
        console.log('WebSocket not available, using polling');
    }
}

function broadcastUpdate(eventType, data) {
    // This would send to WebSocket server
    console.log(`📡 Broadcasting: ${eventType}`, data);

    // For demo, we just log it
    // In production: websocket.send(JSON.stringify({ type: eventType, data }));
}

async function checkForUpdates() {
    try {
        const response = await fetch(`${API_BASE_URL}/crud/stats`);
        if (response.ok) {
            console.log('✓ Polling for updates...');
        }
    } catch (e) {
        // Ignore errors
    }
}

// Initialize WebSocket on load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initWebSocket, 2000);
});

// ============================================
// Auto-Response for Guest Issues
// ============================================

const autoResponseTemplates = {
    late_checkin: "Thank you for letting us know! Late check-in is no problem. Your door code will be active from 3 PM onwards. Please let us know your estimated arrival time.",
    early_checkout: "Thank you for informing us. Early checkout is fine - please leave the keys inside and we wish you safe travels!",
    wifi_issue: "We apologize for the inconvenience. Please try restarting the router (unplug for 10 seconds). If the issue persists, we'll send someone to check it.",
    ac_issue: "Sorry for the discomfort! Please check if the AC is set to COOL mode and temperature below 25°C. If it still doesn't work, we'll send maintenance immediately.",
    noise_complaint: "We're sorry about the disturbance. We'll address this with the other guests right away. Please let us know if it continues.",
    extra_supplies: "Of course! We'll bring extra towels/supplies to your room shortly. Is there a preferred time?",
    checkout_request: "Thank you! Your checkout is confirmed. Please leave the keys inside the room. We hope you enjoyed your stay!",
    default: "Thank you for reaching out! We've received your message and will respond shortly. For urgent matters, please call our front desk."
};

function detectGuestIssueType(message) {
    const msg = message.toLowerCase();

    if (msg.includes('late') && (msg.includes('checkin') || msg.includes('check in') || msg.includes('arrive'))) {
        return 'late_checkin';
    }
    if (msg.includes('early') && (msg.includes('checkout') || msg.includes('check out') || msg.includes('leave'))) {
        return 'early_checkout';
    }
    if (msg.includes('wifi') || msg.includes('internet') || msg.includes('wi-fi')) {
        return 'wifi_issue';
    }
    if (msg.includes('ac') || msg.includes('air condition') || msg.includes('cold') || msg.includes('hot')) {
        return 'ac_issue';
    }
    if (msg.includes('noise') || msg.includes('loud') || msg.includes('noisy')) {
        return 'noise_complaint';
    }
    if (msg.includes('towel') || msg.includes('supply') || msg.includes('soap') || msg.includes('toilet paper')) {
        return 'extra_supplies';
    }
    if (msg.includes('checkout') || msg.includes('check out') || msg.includes('leaving')) {
        return 'checkout_request';
    }

    return 'default';
}

function generateAutoResponse(guestMessage) {
    const issueType = detectGuestIssueType(guestMessage);
    const template = autoResponseTemplates[issueType];

    return {
        issueType,
        response: template,
        requiresAction: ['ac_issue', 'noise_complaint', 'extra_supplies'].includes(issueType)
    };
}

// Demo auto-response function
function demoAutoResponse() {
    const testMessages = [
        "Hi, I'll be arriving late around 11 PM, is that okay?",
        "The WiFi is not working in room 202",
        "The AC in my room is not cooling properly",
        "Can I get some extra towels please?"
    ];

    const message = testMessages[Math.floor(Math.random() * testMessages.length)];
    const response = generateAutoResponse(message);

    openModal('🤖 Auto-Response Demo', `
        <div style="display: grid; gap: 16px;">
            <div>
                <strong>Guest Message:</strong>
                <div style="background: var(--bg-hover); padding: 12px; border-radius: 8px; margin-top: 8px;">
                    "${message}"
                </div>
            </div>
            <div>
                <strong>Detected Issue:</strong> 
                <span class="status-badge confirmed">${response.issueType.replace('_', ' ')}</span>
            </div>
            <div>
                <strong>Auto-Response:</strong>
                <div style="background: var(--bg-hover); padding: 12px; border-radius: 8px; margin-top: 8px; border-left: 3px solid var(--primary);">
                    "${response.response}"
                </div>
            </div>
            ${response.requiresAction ? `
                <div style="color: var(--accent);">
                    ⚠️ This issue requires staff action
                </div>
            ` : ''}
            <button class="btn btn-primary" onclick="demoAutoResponse()">
                🔄 Try Another Message
            </button>
        </div>
    `);
}

console.log('🏨 Hotel PMS Dashboard loaded!');
