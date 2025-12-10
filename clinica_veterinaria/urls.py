

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
    # listar_historiales,
    # crear_historial,
    # detalle_historial,
    # editar_historial,
    # eliminar_historial,

    # Vistas de Reportes
    reportes_view,

    # Vistas de Gestión de Usuarios
    gestion_usuarios,
    crear_usuario,
    crear_veterinario,

        # Vistas de Citas Actuales
    listar_citas_actuales,
    finalizar_cita,
    cancelar_cita,
    
    # Vistas de Ficha Médica
    ficha_medica_paciente,
    agregar_vacuna,
    agregar_cirugia,
    agregar_alergia,
    toggle_alergia,
    
    # Vistas de Pagos
    cuentas_por_cobrar,
    registrar_abono,
    
    # API Endpoints
    dashboard_data,

)

urlpatterns = [
    # --- Administración ---
    path('admin/', admin.site.urls),

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



    # --- Rutas de Ficha Médica ---
    path('paciente/<int:paciente_id>/ficha/', ficha_medica_paciente, name='ficha_medica'),
    path('paciente/<int:paciente_id>/vacuna/agregar/', agregar_vacuna, name='agregar_vacuna'),
    path('paciente/<int:paciente_id>/cirugia/agregar/', agregar_cirugia, name='agregar_cirugia'),
    path('paciente/<int:paciente_id>/alergia/agregar/', agregar_alergia, name='agregar_alergia'),
    path('alergia/<int:alergia_id>/toggle/', toggle_alergia, name='toggle_alergia'),
    
    # --- Rutas de Historial Clínico ---
    # path('historiales/', listar_historiales, name='listar_historiales'),
    # path('historiales/paciente/<int:paciente_id>/', listar_historiales, name='listar_historiales_paciente'),
    # path('historiales/nuevo/', crear_historial, name='crear_historial'),
    # path('historiales/nuevo/cita/<int:cita_id>/', crear_historial, name='crear_historial_cita'),
    # path('historiales/detalle/<int:pk>/', detalle_historial, name='detalle_historial'),
    # path('historiales/editar/<int:pk>/', editar_historial, name='editar_historial'),
    # path('historiales/eliminar/<int:pk>/', eliminar_historial, name='eliminar_historial'),
    
    # --- Rutas de Reportes ---
    path('reportes/', reportes_view, name='reportes'),

    # --- Rutas de Gestión de Usuarios ---
    path('gestion-usuarios/', gestion_usuarios, name='gestion_usuarios'),
    path('gestion-usuarios/nuevo/', crear_usuario, name='crear_usuario'),
    path('gestion-usuarios/veterinario/nuevo/', crear_veterinario, name='crear_veterinario'),

    # --- Rutas de Citas Actuales ---
    path('citas-actuales/', listar_citas_actuales, name='listar_citas_actuales'),
    path('citas-actuales/finalizar/<int:pk>/', finalizar_cita, name='finalizar_cita'),

        # --- Rutas de Citas Actuales ---
    path('citas-actuales/', listar_citas_actuales, name='listar_citas_actuales'),
    path('citas/<int:cita_id>/finalizar/', finalizar_cita, name='finalizar_cita'),
    path('citas/<int:cita_id>/cancelar/', cancelar_cita, name='cancelar_cita'),
    
    # --- Rutas de Ficha Médica ---
    path('paciente/<int:paciente_id>/ficha/', ficha_medica_paciente, name='ficha_medica'),
    path('paciente/<int:paciente_id>/vacuna/agregar/', agregar_vacuna, name='agregar_vacuna'),
    path('paciente/<int:paciente_id>/cirugia/agregar/', agregar_cirugia, name='agregar_cirugia'),
    path('paciente/<int:paciente_id>/alergia/agregar/', agregar_alergia, name='agregar_alergia'),
    path('alergia/<int:alergia_id>/toggle/', toggle_alergia, name='toggle_alergia'),
    
    # --- Rutas de Pagos ---
    path('pagos/cuentas-por-cobrar/', cuentas_por_cobrar, name='cuentas_por_cobrar'),
    path('pagos/<int:pago_id>/abono/', registrar_abono, name='registrar_abono'),
    
    # --- API Dashboard ---
    path('api/dashboard-data/', dashboard_data, name='dashboard_data'),

]