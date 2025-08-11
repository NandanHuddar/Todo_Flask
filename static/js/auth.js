// Authentication utilities

// Check if user is authenticated
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

// Get the authentication token
function getToken() {
    return localStorage.getItem('token');
}

// Set up axios with authentication headers
function setupAxiosAuth() {
    const token = getToken();
    if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login';
    }
}

// Redirect to dashboard if already authenticated
function redirectIfAuthenticated() {
    const urlParams = new URLSearchParams(window.location.search);
    if (isAuthenticated() && !urlParams.has('from_verification')) {
        window.location.href = '/dashboard';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

// Initialize authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    setupAxiosAuth();
    
    // Check current page and apply appropriate auth logic
    const currentPath = window.location.pathname;
    
    if (currentPath === '/dashboard') {
        requireAuth();
    } else if (currentPath === '/login' || currentPath === '/register') {
        redirectIfAuthenticated();
    }
    
    // Set up logout functionality
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    // Update navigation based on auth status
    updateNavigation();
});

// Update navigation based on authentication status
function updateNavigation() {
    const isLoggedIn = isAuthenticated();
    
    // Elements to show/hide based on auth status
    const authElements = document.querySelectorAll('[data-auth]');
    
    authElements.forEach(element => {
        const authRequired = element.getAttribute('data-auth') === 'true';
        
        if ((authRequired && isLoggedIn) || (!authRequired && !isLoggedIn)) {
            element.style.display = 'block';
        } else {
            element.style.display = 'none';
        }
    });
}