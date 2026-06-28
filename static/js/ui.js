/**
 * SIET - UI Module
 * Funcionalidades de interfaz de usuario
 */

document.addEventListener('DOMContentLoaded', function() {
    initTooltips();
    initModals();
    initAlerts();
    initDropdowns();
    initTabs();
    initAccordions();
    initNotifications();
});

/**
 * Inicializar tooltips de Bootstrap
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Inicializar modales de Bootstrap
 */
function initModals() {
    // Confirmación antes de acciones importantes
    document.querySelectorAll('[data-confirm]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.getAttribute('data-confirm');
            const action = this.getAttribute('data-action');
            
            if (confirm(message)) {
                if (action) {
                    window.location.href = action;
                }
            }
        });
    });
    
    // Auto-cerrar modales con Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.querySelector('.modal.show');
            if (modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        }
    });
}

/**
 * Inicializar alertas
 */
function initAlerts() {
    // Auto-cerrar alertas después de un tiempo
    document.querySelectorAll('.alert-auto-dismiss').forEach(alert => {
        const timeout = parseInt(alert.getAttribute('data-dismiss-timeout')) || 5000;
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, timeout);
    });
    
    // Botones de cerrar alertas
    document.querySelectorAll('.alert .btn-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        });
    });
}

/**
 * Inicializar dropdowns
 */
function initDropdowns() {
    const dropdownElementList = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownElementList.forEach(dropdownToggleEl => {
        new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // Cerrar dropdowns al hacer click fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('[data-bs-toggle="dropdown"]')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                const bsDropdown = bootstrap.Dropdown.getInstance(
                    menu.previousElementSibling
                );
                if (bsDropdown) bsDropdown.hide();
            });
        }
    });
}

/**
 * Inicializar tabs
 */
function initTabs() {
    const triggerTabList = document.querySelectorAll('[data-bs-toggle="tab"]');
    triggerTabList.forEach(triggerEl => {
        const tab = new bootstrap.Tab(triggerEl);
        
        triggerEl.addEventListener('click', function(e) {
            e.preventDefault();
            tab.show();
            
            // Guardar tab activo en localStorage
            const tabGroup = this.closest('.nav-tabs');
            if (tabGroup && tabGroup.id) {
                localStorage.setItem(`active-tab-${tabGroup.id}`, this.getAttribute('href'));
            }
        });
    });
    
    // Restaurar tab activo
    document.querySelectorAll('.nav-tabs').forEach(tabGroup => {
        if (tabGroup.id) {
            const activeTab = localStorage.getItem(`active-tab-${tabGroup.id}`);
            if (activeTab) {
                const triggerEl = document.querySelector(`[href="${activeTab}"]`);
                if (triggerEl) {
                    const tab = bootstrap.Tab.getOrCreateInstance(triggerEl);
                    tab.show();
                }
            }
        }
    });
}

/**
 * Inicializar accordions
 */
function initAccordions() {
    // Mantener solo un panel abierto a la vez
    document.querySelectorAll('.accordion-one-open').forEach(accordion => {
        accordion.addEventListener('show.bs.collapse', function(e) {
            const parent = this.closest('.accordion');
            if (parent) {
                parent.querySelectorAll('.collapse.show').forEach(openItem => {
                    if (openItem !== e.target) {
                        const bsCollapse = bootstrap.Collapse.getInstance(openItem);
                        if (bsCollapse) bsCollapse.hide();
                    }
                });
            }
        });
    });
}

/**
 * Mostrar notificación toast
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: success, error, warning, info
 * @param {number} duration - Duración en ms
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const icons = {
        success: 'bi-check-circle-fill',
        error: 'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info: 'bi-info-circle-fill'
    };
    
    const colors = {
        success: 'bg-success',
        error: 'bg-danger',
        warning: 'bg-warning',
        info: 'bg-primary'
    };
    
    const html = `
        <div id="${toastId}" class="toast align-items-center text-white ${colors[type]} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icons[type]} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', html);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Crear contenedor de toasts si no existe
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}

/**
 * Mostrar loading overlay
 * @param {string} message - Mensaje opcional
 */
function showLoading(message = 'Cargando...') {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex flex-column align-items-center justify-content-center';
    overlay.style.cssText = 'background: rgba(255,255,255,0.9); z-index: 9999;';
    overlay.innerHTML = `
        <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted">${message}</p>
    `;
    document.body.appendChild(overlay);
}

/**
 * Ocultar loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Confirmar acción con SweetAlert2
 * @param {object} options - Opciones de confirmación
 * @returns {Promise}
 */
async function confirmAction(options = {}) {
    if (typeof Swal !== 'undefined') {
        return await Swal.fire({
            title: options.title || '¿Está seguro?',
            text: options.text || 'Esta acción no se puede deshacer.',
            icon: options.icon || 'warning',
            showCancelButton: true,
            confirmButtonColor: '#1E3A8A',
            cancelButtonColor: '#6B7280',
            confirmButtonText: options.confirmText || 'Sí, continuar',
            cancelButtonText: options.cancelText || 'Cancelar',
            ...options
        });
    }
    return confirm(options.text || '¿Está seguro?');
}

/**
 * Copiar texto al portapapeles
 * @param {string} text - Texto a copiar
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Texto copiado al portapapeles', 'success');
    } catch (err) {
        // Fallback para navegadores antiguos
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('Texto copiado al portapapeles', 'success');
    }
}

/**
 * Scroll suave a un elemento
 * @param {string} selector - Selector del elemento
 */
function scrollToElement(selector) {
    const element = document.querySelector(selector);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

export { 
    showToast, 
    showLoading, 
    hideLoading, 
    confirmAction, 
    copyToClipboard, 
    scrollToElement 
};
