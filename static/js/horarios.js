// Funcionalidad para seleccionar todos los días en gestión de horarios
function toggleAllDays() {
    const checkboxes = document.querySelectorAll('.dia-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    const btn = document.getElementById('toggleBtn');

    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
    });

    // Actualizar texto del botón
    if (allChecked) {
        btn.innerHTML = '<i class="bi bi-check2-all me-1"></i> Seleccionar todos';
    } else {
        btn.innerHTML = '<i class="bi bi-x-circle me-1"></i> Deseleccionar todos';
    }
}

// Actualizar texto del botón automáticamente cuando cambian los checkboxes
document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.dia-checkbox');
    checkboxes.forEach(cb => {
        cb.addEventListener('change', function () {
            const allChecked = Array.from(checkboxes).every(c => c.checked);
            const btn = document.getElementById('toggleBtn');
            if (allChecked) {
                btn.innerHTML = '<i class="bi bi-x-circle me-1"></i> Deseleccionar todos';
            } else {
                btn.innerHTML = '<i class="bi bi-check2-all me-1"></i> Seleccionar todos';
            }
        });
    });
});
