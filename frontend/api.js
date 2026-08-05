// =====================================================
// STELLARX API CLIENT
// Backend URL: http://127.0.0.1:8081
// =====================================================

const API_BASE_URL = 'http://127.0.0.1:8081';

// =====================================================
// CORE API REQUEST FUNCTION
// =====================================================

async function apiRequest(
    endpoint,
    method = 'GET',
    body = null,
    requiresAuth = false
) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json'
    };

    if (requiresAuth) {
        const token = localStorage.getItem('access_token');

        if (!token) {
            throw new Error('Please login first');
        }

        headers.Authorization = `Bearer ${token}`;
    }

    const options = {
        method,
        headers
    };

    if (body !== null && body !== undefined) {
        options.body = JSON.stringify(body);
    }

    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {
        console.error('Network request failed:', error);
        throw new Error(
            `Cannot connect to backend at ${API_BASE_URL}. Make sure the server is running.`
        );
    }

    if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;

        try {
            const errorData = await response.json();

            if (typeof errorData.detail === 'string') {
                errorMessage = errorData.detail;
            } else if (Array.isArray(errorData.detail)) {
                errorMessage = errorData.detail
                    .map(item => item.msg || JSON.stringify(item))
                    .join(', ');
            } else if (errorData.message) {
                errorMessage = errorData.message;
            } else {
                errorMessage = JSON.stringify(errorData);
            }
        } catch {
            errorMessage = `HTTP ${response.status}`;
        }

        throw new Error(errorMessage);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

// =====================================================
// AUTHENTICATION APIs
// =====================================================

async function apiRegister(
    username,
    firstName,
    lastName,
    email,
    phone,
    password
) {
    return apiRequest(
        '/auth/register',
        'POST',
        {
            username,
            firstName,
            lastName,
            email,
            phone: phone || null,
            password
        }
    );
}

async function apiLogin(email, password) {
    const data = await apiRequest(
        '/auth/login',
        'POST',
        {
            email,
            password
        }
    );

    if (data.access_token) {
        localStorage.setItem(
            'access_token',
            data.access_token
        );

        localStorage.setItem(
            'token_type',
            data.token_type || 'bearer'
        );
    }

    return data;
}

function apiLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user');
    localStorage.removeItem('current_user');
    localStorage.removeItem('current_case_id');
    localStorage.removeItem('current_symptoms');
    localStorage.removeItem('current_analysis_result');

    window.location.href = 'login.html';
}

async function apiGetCurrentUser() {
    return apiRequest(
        '/auth/me',
        'GET',
        null,
        true
    );
}

async function apiChangePassword(
    currentPassword,
    newPassword
) {
    const current = encodeURIComponent(currentPassword);
    const next = encodeURIComponent(newPassword);

    return apiRequest(
        `/auth/change-password?current_password=${current}&new_password=${next}`,
        'POST',
        null,
        true
    );
}

// =====================================================
// CASE APIs
// =====================================================

async function apiCreateCase(
    patientAge,
    patientGender,
    patientLocation
) {
    return apiRequest(
        '/cases/',
        'POST',
        {
            patient_age: Number.parseInt(patientAge, 10),
            patient_gender: patientGender,
            patient_location: patientLocation
        },
        true
    );
}

async function apiListCases(filters = {}) {
    const params = new URLSearchParams();

    if (filters.case_id) {
        params.append('case_id', filters.case_id);
    }

    if (filters.status) {
        params.append('status', filters.status);
    }

    if (filters.start_date) {
        params.append('start_date', filters.start_date);
    }

    if (filters.end_date) {
        params.append('end_date', filters.end_date);
    }

    const query = params.toString();
    const endpoint = query
        ? `/cases/?${query}`
        : '/cases/';

    return apiRequest(
        endpoint,
        'GET',
        null,
        true
    );
}

async function apiGetCase(caseId) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}`,
        'GET',
        null,
        true
    );
}

async function apiUpdateCase(
    caseId,
    patientAge,
    patientGender,
    patientLocation
) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}`,
        'PUT',
        {
            patient_age: Number.parseInt(patientAge, 10),
            patient_gender: patientGender,
            patient_location: patientLocation
        },
        true
    );
}

async function apiDeleteCase(caseId) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}`,
        'DELETE',
        null,
        true
    );
}

// =====================================================
// IMAGE APIs
// =====================================================

async function apiGetCaseImages(caseId) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}/images/`,
        'GET',
        null,
        true
    );
}

// =====================================================
// SYMPTOM APIs
// =====================================================

async function apiSaveSymptoms(caseId, symptomData) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}/symptoms/`,
        'POST',
        symptomData,
        true
    );
}

async function apiGetSymptoms(caseId) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}/symptoms/`,
        'GET',
        null,
        true
    );
}

async function apiUpdateSymptoms(caseId, symptomData) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}/symptoms/`,
        'PUT',
        symptomData,
        true
    );
}

async function apiDeleteSymptoms(caseId) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}/symptoms/`,
        'DELETE',
        null,
        true
    );
}

// =====================================================
// WEIGHTED SYMPTOM ANALYSIS API
// Backend route:
// POST /cases/{case_id}/analysis/
// =====================================================

async function apiRunAnalysis(caseId) {
    return apiRequest(
        `/cases/${encodeURIComponent(caseId)}/analysis/`,
        'POST',
        null,
        true
    );
}

// Optional compatibility alias
async function apiAnalyzeCase(caseId) {
    return apiRunAnalysis(caseId);
}

// =====================================================
// HELPER FUNCTIONS
// =====================================================

function getCurrentUser() {
    const userString =
        localStorage.getItem('user') ||
        localStorage.getItem('current_user');

    if (!userString) {
        return null;
    }

    try {
        return JSON.parse(userString);
    } catch {
        return null;
    }
}

function isAuthenticated() {
    return Boolean(
        localStorage.getItem('access_token')
    );
}

function redirectToLogin() {
    window.location.href = 'login.html';
}

function redirectToDashboard() {
    window.location.href = 'dashboard.html';
}