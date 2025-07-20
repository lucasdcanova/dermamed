// API Configuration
const API_URL = 'http://localhost:8000';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// DOM Elements
const loginModal = document.getElementById('login-modal');
const authBtn = document.getElementById('auth-btn');
const userInfo = document.getElementById('user-info');
const fileInput = document.getElementById('file-input');
const uploadArea = document.getElementById('upload-area');
const preview = document.getElementById('preview');
const analyzeBtn = document.getElementById('analyze-btn');
const demoBtn = document.getElementById('demo-btn');
const resultsSection = document.getElementById('results-section');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Auth
    authBtn.addEventListener('click', handleAuthClick);
    document.querySelector('.close').addEventListener('click', () => {
        loginModal.style.display = 'none';
    });
    document.getElementById('login-form').addEventListener('submit', handleLogin);

    // File Upload
    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', handleFileDrop);

    // Buttons
    analyzeBtn.addEventListener('click', handleAnalyze);
    demoBtn.addEventListener('click', handleDemo);
}

// Authentication
async function checkAuth() {
    if (authToken) {
        try {
            const response = await fetch(`${API_URL}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                currentUser = await response.json();
                updateAuthUI(true);
            } else {
                logout();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            logout();
        }
    }
}

function handleAuthClick() {
    if (currentUser) {
        logout();
    } else {
        loginModal.style.display = 'block';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch(`${API_URL}/api/v1/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            loginModal.style.display = 'none';
            await checkAuth();
        } else {
            alert('Login falhou. Verifique suas credenciais.');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Erro ao fazer login. Tente novamente.');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    updateAuthUI(false);
}

function updateAuthUI(isAuthenticated) {
    if (isAuthenticated) {
        userInfo.textContent = `Dr. ${currentUser.username}`;
        authBtn.textContent = 'Logout';
    } else {
        userInfo.textContent = 'Não autenticado';
        authBtn.textContent = 'Login';
    }
}

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        displayPreview(file);
    }
}

function handleFileDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        fileInput.files = e.dataTransfer.files;
        displayPreview(file);
    }
}

function displayPreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        document.querySelector('.upload-prompt').style.display = 'none';
        analyzeBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// Analysis
async function handleAnalyze() {
    if (!authToken) {
        alert('Por favor, faça login primeiro.');
        loginModal.style.display = 'block';
        return;
    }
    
    const file = fileInput.files[0];
    if (!file) {
        alert('Por favor, selecione uma imagem.');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Add clinical data
    const clinicalData = {
        patient_age: document.getElementById('patient-age').value,
        patient_sex: document.getElementById('patient-sex').value,
        lesion_location: document.getElementById('lesion-location').value,
        symptoms_duration: document.getElementById('symptoms-duration').value,
        clinical_history: document.getElementById('clinical-history').value
    };
    
    Object.entries(clinicalData).forEach(([key, value]) => {
        if (value) {
            formData.append(key, value);
        }
    });
    
    // Show loading state
    analyzeBtn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-block';
    
    try {
        const response = await fetch(`${API_URL}/api/v1/analysis/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            displayResults(result);
        } else {
            const error = await response.json();
            alert(`Erro na análise: ${error.detail || 'Erro desconhecido'}`);
        }
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Erro ao analisar imagem. Tente novamente.');
    } finally {
        // Reset button state
        analyzeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    }
}

async function handleDemo() {
    try {
        const response = await fetch(`${API_URL}/api/v1/analysis/demo`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            displayResults(result);
        } else {
            alert('Erro ao carregar demonstração.');
        }
    } catch (error) {
        console.error('Demo error:', error);
        alert('Erro ao carregar demonstração.');
    }
}

// Display Results
function displayResults(result) {
    resultsSection.style.display = 'block';
    
    // Disclaimer
    document.getElementById('disclaimer').textContent = result.compliance.disclaimer;
    
    // Primary Diagnosis
    const analysis = result.analysis;
    document.getElementById('primary-diagnosis-text').textContent = analysis.primary_diagnosis;
    
    // Confidence
    const confidencePercent = Math.round(analysis.confidence * 100);
    document.getElementById('confidence-fill').style.width = `${confidencePercent}%`;
    document.getElementById('confidence-text').textContent = `${confidencePercent}%`;
    
    // Risk Assessment
    const riskElement = document.getElementById('risk-assessment');
    riskElement.textContent = analysis.risk_assessment;
    riskElement.className = 'risk-badge';
    
    if (analysis.risk_assessment.toLowerCase().includes('low')) {
        riskElement.classList.add('risk-low');
    } else if (analysis.risk_assessment.toLowerCase().includes('high')) {
        riskElement.classList.add('risk-high');
    } else {
        riskElement.classList.add('risk-medium');
    }
    
    // Biopsy Recommendation
    const biopsyText = analysis.requires_biopsy ? 
        '⚠️ Biópsia recomendada' : 
        '✓ Biópsia não necessária no momento';
    document.getElementById('biopsy-recommendation').textContent = biopsyText;
    
    // ABCDE Criteria
    if (analysis.lesion_characteristics) {
        document.getElementById('abcde-card').style.display = 'block';
        const chars = analysis.lesion_characteristics;
        
        if (chars.asymmetry !== null) {
            document.getElementById('asymmetry-bar').style.width = `${chars.asymmetry * 100}%`;
            document.getElementById('asymmetry-value').textContent = chars.asymmetry.toFixed(2);
        }
        
        if (chars.border_irregularity !== null) {
            document.getElementById('border-bar').style.width = `${chars.border_irregularity * 100}%`;
            document.getElementById('border-value').textContent = chars.border_irregularity.toFixed(2);
        }
        
        if (chars.color_variation !== null) {
            document.getElementById('color-bar').style.width = `${chars.color_variation * 100}%`;
            document.getElementById('color-value').textContent = chars.color_variation.toFixed(2);
        }
        
        if (chars.diameter_mm !== null) {
            document.getElementById('diameter-value').textContent = `${chars.diameter_mm.toFixed(1)}mm`;
        }
    }
    
    // Differential Diagnoses
    const diffList = document.getElementById('differential-list');
    diffList.innerHTML = '';
    analysis.differential_diagnoses.forEach(diff => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${diff.condition}</strong> - ${(diff.probability * 100).toFixed(1)}%`;
        if (diff.icd10_code) {
            li.innerHTML += ` <small>(${diff.icd10_code})</small>`;
        }
        diffList.appendChild(li);
    });
    
    // Recommendations
    const recList = document.getElementById('recommendations-list');
    recList.innerHTML = '';
    analysis.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = `• ${rec}`;
        recList.appendChild(li);
    });
    
    // Follow-up
    document.getElementById('follow-up-interval').textContent = analysis.follow_up_interval || 'Conforme indicação clínica';
    
    // Metadata
    document.getElementById('analysis-id').textContent = result.id;
    document.getElementById('processing-time').textContent = 
        result.processing_time_seconds ? result.processing_time_seconds.toFixed(2) : '-';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}