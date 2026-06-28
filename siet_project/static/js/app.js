/**
 * SIET - Aplicación JavaScript Principal
 */

// ==================== CONFIGURACIÓN ====================
const API_BASE = '/api/v1';
let currentUser = null;
let currentSession = null;

// ==================== UTILIDADES ====================

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function getToken() {
    return localStorage.getItem('access_token');
}

async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error en la petición');
    }
    
    return response.json();
}

// ==================== AUTENTICACIÓN ====================

function showLoginModal() {
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
}

function showRegisterModal() {
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
}

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        localStorage.setItem('access_token', data.access_token);
        currentUser = data.user;
        
        Swal.fire({
            icon: 'success',
            title: '¡Bienvenido!',
            text: `Hola, ${currentUser.full_name}`
        }).then(() => {
            window.location.href = '/dashboard';
        });
        
        bootstrap.Modal.getInstance(document.getElementById('loginModal')).hide();
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error de autenticación',
            text: error.message
        });
    }
});

document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userData = {
        username: document.getElementById('regUsername').value,
        email: document.getElementById('regEmail').value,
        first_name: document.getElementById('regFirstName').value,
        last_name: document.getElementById('regLastName').value,
        password: document.getElementById('regPassword').value,
        role_id: 3  // Por defecto Estudiante
    };
    
    try {
        const user = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        Swal.fire({
            icon: 'success',
            title: 'Registro exitoso',
            text: 'Ahora puedes iniciar sesión'
        }).then(() => {
            bootstrap.Modal.getInstance(document.getElementById('registerModal')).hide();
            showLoginModal();
        });
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error de registro',
            text: error.message
        });
    }
});

// ==================== CONSENTIMIENTO ====================

async function checkConsent(userId) {
    try {
        const result = await apiRequest(`/consent/check/${userId}`);
        return result.has_consent && result.accepted;
    } catch (error) {
        return false;
    }
}

async function giveConsent(userId) {
    try {
        await apiRequest('/consent/', {
            method: 'POST',
            body: JSON.stringify({
                user_id: userId,
                accepted: true
            })
        });
        return true;
    } catch (error) {
        console.error('Error al dar consentimiento:', error);
        return false;
    }
}

// ==================== SESIONES ====================

async function startSession(userId) {
    try {
        const session = await apiRequest('/sessions/', {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });
        currentSession = session;
        return session;
    } catch (error) {
        console.error('Error al iniciar sesión:', error);
        return null;
    }
}

// ==================== NAVEGACIÓN ====================

function updateNavMenu() {
    const navMenu = document.getElementById('navMenu');
    if (!navMenu) return;
    
    if (currentUser) {
        navMenu.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="/dashboard">
                    <i class="bi bi-speedometer2"></i> Dashboard
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="logout()">
                    <i class="bi bi-box-arrow-right"></i> Salir
                </a>
            </li>
        `;
    } else {
        navMenu.innerHTML = `
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="showLoginModal()">
                    <i class="bi bi-box-arrow-in-right"></i> Login
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="#" onclick="showRegisterModal()">
                    <i class="bi bi-person-plus"></i> Registro
                </a>
            </li>
        `;
    }
}

function logout() {
    localStorage.removeItem('access_token');
    currentUser = null;
    currentSession = null;
    updateNavMenu();
    window.location.href = '/';
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    updateNavMenu();
    
    // Verificar si hay token almacenado
    const token = getToken();
    if (token) {
        apiRequest('/auth/me')
            .then(user => {
                currentUser = user;
                updateNavMenu();
            })
            .catch(() => {
                localStorage.removeItem('access_token');
            });
    }
});

// ==================== BEHAVIORAL ANALYTICS ====================

class BehaviorTracker {
    constructor(userId, sessionId) {
        this.userId = userId;
        this.sessionId = sessionId;
        this.init();
    }
    
    init() {
        // Mouse move
        document.addEventListener('mousemove', (e) => this.logEvent('mousemove', e));
        
        // Scroll
        document.addEventListener('scroll', () => this.logEvent('scroll'));
        
        // Focus/Blur
        window.addEventListener('focus', () => this.logEvent('focus'));
        window.addEventListener('blur', () => this.logEvent('blur'));
        
        // Visibility change
        document.addEventListener('visibilitychange', () => {
            this.logEvent('visibilitychange');
        });
        
        // Click
        document.addEventListener('click', (e) => this.logEvent('click', e));
        
        // Keyboard
        document.addEventListener('keydown', (e) => this.logEvent('keydown', e));
    }
    
    async logEvent(eventType, event) {
        const eventData = {
            user_id: this.userId,
            session_id: this.sessionId,
            event_type: eventType,
            x_coordinate: event?.clientX || null,
            y_coordinate: event?.clientY || null,
            scroll_position: window.scrollY || null,
            element_id: event?.target?.id || null,
            page_url: window.location.href,
            timestamp: new Date().toISOString()
        };
        
        try {
            await apiRequest('/analytics/behavior/log', {
                method: 'POST',
                body: JSON.stringify(eventData)
            });
        } catch (error) {
            // Silent fail para no molestar al usuario
        }
    }
}
