const API_BASE_URL = 'http://127.0.0.1:8081';

async function apiRequest(endpoint, method = 'GET', body = null, requiresAuth = false) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
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
    headers,
  };

  if (body !== null && body !== undefined) {
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    console.error('Network request failed:', error);
    throw new Error(`Cannot connect to backend at ${API_BASE_URL}. Make sure the server is running.`);
  }

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((item) => item.msg || JSON.stringify(item)).join(', ');
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

export const api = {
  // Auth
  register: (username, firstName, lastName, email, phone, password) =>
    apiRequest('/auth/register', 'POST', { username, firstName, lastName, email, phone: phone || null, password }),
  
  login: async (email, password) => {
    const data = await apiRequest('/auth/login', 'POST', { email, password });
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('token_type', data.token_type || 'bearer');
    }
    return data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user');
    localStorage.removeItem('current_user');
    localStorage.removeItem('current_case_id');
    localStorage.removeItem('current_symptoms');
    localStorage.removeItem('current_analysis_result');
    window.location.href = '/login';
  },

  getCurrentUser: () => apiRequest('/auth/me', 'GET', null, true),

  changePassword: (currentPassword, newPassword) => {
    const current = encodeURIComponent(currentPassword);
    const next = encodeURIComponent(newPassword);
    return apiRequest(`/auth/change-password?current_password=${current}&new_password=${next}`, 'POST', null, true);
  },

  // Cases
  createCase: (patientAge, patientGender, patientLocation) =>
    apiRequest('/cases/', 'POST', { patient_age: Number.parseInt(patientAge, 10), patient_gender: patientGender, patient_location: patientLocation }, true),

  listCases: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.case_id) params.append('case_id', filters.case_id);
    if (filters.status) params.append('status', filters.status);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    
    const query = params.toString();
    const endpoint = query ? `/cases/?${query}` : '/cases/';
    return apiRequest(endpoint, 'GET', null, true);
  },

  getCase: (caseId) => apiRequest(`/cases/${encodeURIComponent(caseId)}`, 'GET', null, true),

  updateCase: (caseId, patientAge, patientGender, patientLocation) =>
    apiRequest(`/cases/${encodeURIComponent(caseId)}`, 'PUT', { patient_age: Number.parseInt(patientAge, 10), patient_gender: patientGender, patient_location: patientLocation }, true),

  deleteCase: (caseId) => apiRequest(`/cases/${encodeURIComponent(caseId)}`, 'DELETE', null, true),

  // Images
  getCaseImages: (caseId) => apiRequest(`/cases/${encodeURIComponent(caseId)}/images/`, 'GET', null, true),
  uploadCaseImages: async (caseId, images) => {
    // We send base64 data directly as JSON to bypass FormData browser bugs
    const payload = {
      images: images.map(img => ({
        name: img.name || 'image.jpg',
        data: img.data
      }))
    };

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/cases/${encodeURIComponent(caseId)}/images/base64`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      let errorMsg = 'Failed to upload images';
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorMsg;
      } catch (e) {}
      throw new Error(errorMsg);
    }
    return response.json();
  },

  // Symptoms
  saveSymptoms: (caseId, symptomData) => apiRequest(`/cases/${encodeURIComponent(caseId)}/symptoms/`, 'POST', symptomData, true),
  getSymptoms: (caseId) => apiRequest(`/cases/${encodeURIComponent(caseId)}/symptoms/`, 'GET', null, true),
  updateSymptoms: (caseId, symptomData) => apiRequest(`/cases/${encodeURIComponent(caseId)}/symptoms/`, 'PUT', symptomData, true),
  deleteSymptoms: (caseId) => apiRequest(`/cases/${encodeURIComponent(caseId)}/symptoms/`, 'DELETE', null, true),

  // Analysis
  runAnalysis: (caseId) => apiRequest(`/cases/${encodeURIComponent(caseId)}/analysis/`, 'POST', null, true),

  // Helpers
  isAuthenticated: () => Boolean(localStorage.getItem('access_token')),
  getUser: () => {
    const userString = localStorage.getItem('user') || localStorage.getItem('current_user');
    if (!userString) return null;
    try {
      return JSON.parse(userString);
    } catch {
      return null;
    }
  }
};
