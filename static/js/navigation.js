/**
 * SIET - Navigation Module
 * Manejo de navegación y menú lateral
 */

document.addEventListener('DOMContentLoaded', function() {
    initSidebar();
    initMobileMenu();
    initBreadcrumbs();
    initActiveNavigation();
});

/**
 * Inicializar sidebar
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar-siet');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle('show');
            }
        });
    }
    
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }
    
    // Cerrar sidebar con tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('show');
            }
        }
    });
}

/**
 * Inicializar menú móvil
 */
function initMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
            this.setAttribute('aria-expanded', 
                this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
            );
        });
    }
}

/**
 * Inicializar breadcrumbs dinámicos
 */
function initBreadcrumbs() {
    const breadcrumbContainer = document.querySelector('.breadcrumb-container');
    if (!breadcrumbContainer) return;
    
    const path = window.location.pathname;
    const segments = path.split('/').filter(segment => segment !== '');
    
    let html = '<nav aria-label="breadcrumb"><ol class="breadcrumb breadcrumb-siet">';
    html += '<li class="breadcrumb-item"><a href="/">Inicio</a></li>';
    
    segments.forEach((segment, index) => {
        const url = '/' + segments.slice(0, index + 1).join('/');
        const isLast = index === segments.length - 1;
        const name = segment.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        if (isLast) {
            html += `<li class="breadcrumb-item active" aria-current="page">${name}</li>`;
        } else {
            html += `<li class="breadcrumb-item"><a href="${url}">${name}</a></li>`;
        }
    });
    
    html += '</ol></nav>';
    breadcrumbContainer.innerHTML = html;
}

/**
 * Resaltar navegación activa
 */
function initActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-menu-link, .nav-link-siet');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && (currentPath === href || currentPath.startsWith(href + '/'))) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
        } else {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
        }
    });
}

/**
 * Navegar a una página
 * @param {string} url - URL de destino
 */
function navigateTo(url) {
    window.location.href = url;
}

/**
 * Actualizar estado de navegación
 * @param {string} title - Título de la página
 * @param {string} url - URL actual
 */
function updateNavigationState(title, url) {
    document.title = `${title} - SIET`;
    if (window.history && window.history.pushState) {
        window.history.pushState({ page: url }, title, url);
        initActiveNavigation();
        initBreadcrumbs();
    }
}

/**
 * Prevenir navegación si hay cambios sin guardar
 * @param {boolean} hasUnsavedChanges - Si hay cambios sin guardar
 */
function preventUnsavedNavigation(hasUnsavedChanges) {
    if (hasUnsavedChanges) {
        window.addEventListener('beforeunload', function(e) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        });
    } else {
        window.removeEventListener('beforeunload', preventUnsavedNavigation);
    }
}

export { 
    navigateTo, 
    updateNavigationState, 
    preventUnsavedNavigation 
};
