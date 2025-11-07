// static/js/theme.js
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIconLight = document.getElementById('theme-icon-light');
    const themeIconDark = document.getElementById('theme-icon-dark');
    
    function updateThemeIcons(theme) {
        if (theme === 'dark') {
            if (themeIconLight) themeIconLight.classList.add('d-none');
            if (themeIconDark) themeIconDark.classList.remove('d-none');
        } else {
            if (themeIconLight) themeIconLight.classList.remove('d-none');
            if (themeIconDark) themeIconDark.classList.add('d-none');
        }
    }
    
    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        updateThemeIcons(theme);
    }
    
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }
    
    // Initialize theme
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        setTheme(storedTheme);
    } else {
        // Default to light theme
        setTheme('light');
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Cerrar sidebar en móvil
    const sidebarLinks = document.querySelectorAll('#sidebarCollapse .nav-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                const collapse = new bootstrap.Collapse(document.getElementById('sidebarCollapse'));
                collapse.hide();
            }
        });
    });
});