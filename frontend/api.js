// =====================================================
// STELLARX API CLIENT
// Backend URL: http://127.0.0.1:8080
// =====================================================

const API_BASE_URL = 'http://127.0.0.1:8080';

// =====================================================
// CORE API REQUEST FUNCTION
// =====================================================

async function apiRequest(endpoint, method = 'GET', body = null, requiresAuth = false) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
    };
    
    // Add Authorization header if required
    if (requiresAuth) {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('Please login first');
        }
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
        method: method,
        headers: headers,
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error: ${response.status}`);
    }
    
    return response.json();
}

// =====================================================
// AUTHENTICATION APIS
// =====================================================

async function apiRegister(username, firstName, lastName, email, phone, password) {
    return apiRequest('/auth/register', 'POST', {
        username,
        firstName,
        lastName,
        email,
        phone: phone || null,
        password
    });
}

async function apiLogin(email, password) {
    const data = await apiRequest('/auth/login', 'POST', {
        email,
        password
    });
    
    if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type || 'bearer');
    }
    
    return data;
}

function apiLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

async function apiGetCurrentUser() {
    return apiRequest('/auth/me', 'GET', null, true);
}

// =====================================================
// CASE APIS
// =====================================================

async function apiCreateCase(patient_age, patient_gender, patient_location) {
    return apiRequest('/cases/', 'POST', {
        patient_age: parseInt(patient_age),
        patient_gender: patient_gender,
        patient_location: patient_location
    }, true);
}

async function apiListCases() {
    return apiRequest('/cases/', 'GET', null, true);
}

async function apiGetCase(caseId) {
    return apiRequest(`/cases/${caseId}`, 'GET', null, true);
}

async function apiUpdateCase(caseId, patient_age, patient_gender, patient_location) {
    return apiRequest(`/cases/${caseId}`, 'PUT', {
        patient_age: parseInt(patient_age),
        patient_gender: patient_gender,
        patient_location: patient_location
    }, true);
}

async function apiDeleteCase(caseId) {
    return apiRequest(`/cases/${caseId}`, 'DELETE', null, true);
}

// =====================================================
// HELPER FUNCTIONS
// =====================================================

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
        return JSON.parse(userStr);
    } catch {
        return null;
    }
}

function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

function redirectToLogin() {
    window.location.href = 'login.html';
}

function redirectToDashboard() {
    window.location.href = 'dashboard.html';
}