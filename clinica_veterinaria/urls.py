# clinica_veterinaria/urls.py

from django.contrib import admin
from django.urls import path
from core.views import (
    login_view, 
    panel_view, 
    logout_view,
    
    # Vistas de Citas
    listar_citas,
    crear_cita,
    editar_cita,
    eliminar_cita,
    detalle_cita,
    confirmar_cita,

    # Vistas de Tutores
    listar_tutores,
    crear_tutor,
    editar_tutor,
    eliminar_tutor,

    # Vistas de Pacientes
    listar_pacientes,
    crear_paciente,
    editar_paciente,
    eliminar_paciente,

    # Vistas de Horarios
    listar_horarios_vet,
    gestionar_horarios,
    eliminar_horario,

    # NUEVAS VISTAS DE PERSONAL
    gestionar_personal,
    eliminar_personal,

    # Vistas de Historial Clínico
    listar_historiales,
    crear_historial,
    detalle_historial,
    editar_historial,
    eliminar_historial,

    # Vistas de Reportes
    reportes_view,
)

urlpatterns = [
    # --- Administración (Deshabilitado - usar interfaz personalizada) ---
    # path('admin/', admin.site.urls),  # Comentado: usar /personal/ en su lugar

    # --- Autenticación ---
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('panel/', panel_view, name='panel'),

    # --- Página principal (raíz del sitio) ---
    path('', login_view, name='home'),

    # --- Rutas del CRUD de Citas ---
    path('agenda/', listar_citas, name='listar_citas'),
    path('agenda/nueva/', crear_cita, name='crear_cita'),
    path('agenda/detalle/<int:pk>/', detalle_cita, name='detalle_cita'),
    path('agenda/editar/<int:pk>/', editar_cita, name='editar_cita'),
    path('agenda/cancelar/<int:pk>/', eliminar_cita, name='eliminar_cita'),
    path('agenda/confirmar/<int:pk>/', confirmar_cita, name='confirmar_cita'),

    # --- Rutas CRUD Tutores ---
    path('tutores/', listar_tutores, name='listar_tutores'),
    path('tutores/nuevo/', crear_tutor, name='crear_tutor'),
    path('tutores/editar/<int:pk>/', editar_tutor, name='editar_tutor'),
    path('tutores/eliminar/<int:pk>/', eliminar_tutor, name='eliminar_tutor'),

    # --- Rutas CRUD Pacientes ---
    path('pacientes/', listar_pacientes, name='listar_pacientes'),
    path('pacientes/nuevo/', crear_paciente, name='crear_paciente'),
    path('pacientes/editar/<int:pk>/', editar_paciente, name='editar_paciente'),
    path('pacientes/eliminar/<int:pk>/', eliminar_paciente, name='eliminar_paciente'),

    # --- Rutas de Gestión de Horarios ---
    path('horarios/', listar_horarios_vet, name='listar_horarios_vet'),
    path('horarios/gestionar/<str:vet_id>/', gestionar_horarios, name='gestionar_horarios'),
    path('horarios/eliminar/<int:pk>/', eliminar_horario, name='eliminar_horario'),
    
    # --- Rutas de Gestión de Personal ---
    path('personal/', gestionar_personal, name='gestionar_personal'),
    path('personal/eliminar/<int:pk>/', eliminar_personal, name='eliminar_personal'),
    
    # --- Rutas de Historial Clínico ---
    path('historiales/', listar_historiales, name='listar_historiales'),
    path('historiales/paciente/<int:paciente_id>/', listar_historiales, name='listar_historiales_paciente'),
    path('historiales/nuevo/', crear_historial, name='crear_historial'),
    path('historiales/nuevo/cita/<int:cita_id>/', crear_historial, name='crear_historial_cita'),
    path('historiales/detalle/<int:pk>/', detalle_historial, name='detalle_historial'),
    path('historiales/editar/<int:pk>/', editar_historial, name='editar_historial'),
    path('historiales/eliminar/<int:pk>/', eliminar_historial, name='eliminar_historial'),
    
    # --- Rutas de Reportes ---
    path('reportes/', reportes_view, name='reportes'),
]