// static/js/theme.js

(() => {
    'use strict';

    // Función para obtener el tema guardado en localStorage
    const getStoredTheme = () => localStorage.getItem('theme');
    
    // Función para guardar el tema en localStorage
    const setStoredTheme = theme => localStorage.setItem('theme', theme);

    // Función para obtener el tema preferido (guardado o del sistema)
    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme();
        if (storedTheme) {
            return storedTheme;
        }
        // Si no hay nada guardado, usa la preferencia del sistema (modo oscuro)
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };

    // Función para aplicar el tema al HTML
    const setTheme = theme => {
        document.documentElement.setAttribute('data-bs-theme', theme);
    };

    // Aplicamos el tema preferido al cargar la página
    setTheme(getPreferredTheme());

    // --- Lógica del Botón de Toggle ---
    
    // Espera a que el DOM esté cargado para encontrar los botones
    window.addEventListener('DOMContentLoaded', () => {
        // Busca todos los botones de toggle (podemos tener uno en el panel y otro en el login)
        document.querySelectorAll('#theme-toggle').forEach(toggle => {
            toggle.addEventListener('click', () => {
                const currentTheme = getStoredTheme() || getPreferredTheme();
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                setStoredTheme(newTheme);
                setTheme(newTheme);
            });
        });
    });
})();