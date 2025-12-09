

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse 
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

# Importamos todos los Modelos y Forms que usaremos
from .models import (
    Usuario, Cita, Tutor, Paciente, Veterinario, HorarioDisponible,
    HistorialClinico, Vacuna, Cirugia, Alergia
)
from .forms import (
    CitaForm, TutorForm, PacienteForm, HorarioForm, PersonalForm,
    VeterinarioForm, CitaFinalizarForm, ReporteForm,
    VacunaForm, CirugiaForm, AlergiaForm, HorarioMultipleForm
)

# -----------------------------------------------------------------
# VISTAS DE AUTENTICACIÓN
# -----------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('panel')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password) 
        if user is not None:
            login(request, user)
            return redirect('panel')
        else:
            context = {'error': 'Email o contraseña incorrectos.'}
            return render(request, 'core/login.html', context)
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# -----------------------------------------------------------------
# VISTAS DEL PANEL
# -----------------------------------------------------------------

@login_required(login_url='login')
def panel_view(request):
    # Solo mostrar dashboard con estadísticas si es ADMIN
    if request.user.rol == 'ADMIN':
        try:
            # Estadísticas para el dashboard
            total_pacientes = Paciente.objects.count()
            total_veterinarios = Veterinario.objects.count()
            citas_pendientes = Cita.objects.filter(
                estado__in=['SOLICITADA', 'AGENDADA']
            ).count()
            citas_hoy = Cita.objects.filter(
                fecha_hora__date=timezone.localdate()
            ).count()
        except Exception as e:
            # Si hay error con la BD, usar valores por defecto
            total_pacientes = 0
            total_veterinarios = 0
            citas_pendientes = 0
            citas_hoy = 0
        
        context = {
            'total_pacientes': total_pacientes,
            'total_veterinarios': total_veterinarios,
            'citas_pendientes': citas_pendientes,
            'citas_hoy': citas_hoy,
        }
        return render(request, 'core/panel.html', context)
    else:
        # Para otros roles, redirigir a agenda (comportamiento original)
        return redirect('listar_citas')

# --- CRUD CITAS ---

@login_required(login_url='login')
def listar_citas(request):
    date_str = request.GET.get('fecha', None)
    if date_str:
        try:
            current_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.localdate()
    else:
        current_date = timezone.localdate()
    previous_day = current_date - timedelta(days=1)
    next_day = current_date + timedelta(days=1)
    vet_id = request.GET.get('veterinario', None)
    veterinarios = Veterinario.objects.all()
    citas = Cita.objects.filter(fecha_hora__date=current_date)
    
    if vet_id:
        citas = citas.filter(veterinario=vet_id) 
    
    citas = citas.order_by('fecha_hora')
    context = {
        'citas': citas,
        'current_date': current_date,
        'previous_day': previous_day,
        'next_day': next_day,
        'veterinarios': veterinarios,
        'selected_vet_id': int(vet_id) if vet_id else None
    }
    return render(request, 'core/listar_citas.html', context)

@login_required(login_url='login')
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita_guardada = form.save(commit=False)
            cita_guardada.creada_por = request.user 
            if request.user.rol == 'VETERINARIO':
                cita_guardada.estado = 'SOLICITADA'
            else:
                cita_guardada.estado = 'AGENDADA'
            cita_guardada.save() 
            fecha_cita = cita_guardada.fecha_hora.date().strftime('%Y-%m-%d')
            return redirect(f"{reverse('listar_citas')}?fecha={fecha_cita}")
    else:
        form = CitaForm()
    return render(request, 'core/cita_form.html', {'form': form}) 

@login_required(login_url='login')
def editar_cita(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_citas')
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            cita_guardada = form.save()
            fecha_cita = cita_guardada.fecha_hora.date().strftime('%Y-%m-%d')
            return redirect(f"{reverse('listar_citas')}?fecha={fecha_cita}")
    else:
        form = CitaForm(instance=cita)
    return render(request, 'core/cita_form.html', {'form': form})

@login_required(login_url='login')
def eliminar_cita(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_citas')
    cita = get_object_or_404(Cita, pk=pk)
    fecha_cita = cita.fecha_hora.date().strftime('%Y-%m-%d')
    if request.method == 'POST':
        cita.delete()
        return redirect(f"{reverse('listar_citas')}?fecha={fecha_cita}")
    return render(request, 'core/cita_confirmar_eliminar.html', {'cita': cita})

@login_required(login_url='login')
def detalle_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    context = {
        'cita': cita,
        'fecha_agenda': cita.fecha_hora.date().strftime('%Y-%m-%d')
    }
    return render(request, 'core/detalle_cita.html', context)

@login_required(login_url='login')
@require_POST
def confirmar_cita(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('panel')
    cita = get_object_or_404(Cita, pk=pk, estado='SOLICITADA')
    cita.estado = 'AGENDADA' 
    cita.save()
    fecha_cita = cita.fecha_hora.date().strftime('%Y-%m-%d')
    return redirect(f"{reverse('listar_citas')}?fecha={fecha_cita}")

# --- CRUD TUTORES ---
@login_required(login_url='login')
def listar_tutores(request):
    tutores = Tutor.objects.all()
    return render(request, 'core/listar_tutores.html', {'tutores': tutores})

@login_required(login_url='login')
def crear_tutor(request):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_tutores')
    if request.method == 'POST':
        form = TutorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_tutores')
    else:
        form = TutorForm()
    return render(request, 'core/tutor_form.html', {'form': form})

@login_required(login_url='login')
def editar_tutor(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_tutores')
    tutor = get_object_or_404(Tutor, pk=pk) 
    if request.method == 'POST':
        form = TutorForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            return redirect('listar_tutores')
    else:
        form = TutorForm(instance=tutor)
    return render(request, 'core/tutor_form.html', {'form': form})

@login_required(login_url='login')
def eliminar_tutor(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_tutores')
    tutor = get_object_or_404(Tutor, pk=pk)
    if request.method == 'POST':
        tutor.delete()
        return redirect('listar_tutores')
    return render(request, 'core/tutor_confirmar_eliminar.html', {'tutor': tutor})

# --- CRUD PACIENTES ---
@login_required(login_url='login')
def listar_pacientes(request):
    pacientes = Paciente.objects.all()
    return render(request, 'core/listar_pacientes.html', {'pacientes': pacientes})

@login_required(login_url='login')
def crear_paciente(request):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_pacientes') 
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'core/paciente_form.html', {'form': form})

@login_required(login_url='login')
def editar_paciente(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_pacientes')
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('listar_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'core/paciente_form.html', {'form': form})

@login_required(login_url='login')
def eliminar_paciente(request, pk):
    if request.user.rol not in ['ADMIN', 'RECEPCIONISTA']:
        return redirect('listar_pacientes')
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('listar_pacientes')
    return render(request, 'core/paciente_confirmar_eliminar.html', {'paciente': paciente})

# ============================================================================
# VISTAS: GESTIÓN DE HORARIOS (Solo Admin)
# ============================================================================

@login_required(login_url='login')
def listar_horarios_vet(request):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    veterinarios = Veterinario.objects.all()
    context = { 'veterinarios': veterinarios }
    return render(request, 'core/listar_horarios_vet.html', context)

@login_required(login_url='login')
def gestionar_horarios(request, vet_id):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    veterinario = get_object_or_404(Veterinario, pk=vet_id)
    
    if request.method == 'POST':
        form = HorarioMultipleForm(request.POST)
        if form.is_valid():
            dias_seleccionados = form.cleaned_data['dias_semana']
            hora_inicio = form.cleaned_data['hora_inicio']
            hora_fin = form.cleaned_data['hora_fin']
            
            creados = 0
            errores = []
            
            for dia in dias_seleccionados:
                horario = HorarioDisponible(
                    veterinario=veterinario,
                    dia_semana=int(dia),
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin
                )
                try:
                    horario.full_clean()
                    horario.save()
                    creados += 1
                except ValidationError as e:
                    # Nombre del día
                    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    dia_nombre = dias_nombres[int(dia)]
                    errores.append(f"{dia_nombre}: {', '.join(e.messages)}")
            
            if creados > 0:
                from django.contrib import messages
                messages.success(request, f"✓ Se crearon {creados} horario(s) correctamente")
            if errores:
                from django.contrib import messages
                for error in errores:
                    messages.warning(request, f"⚠ {error}")
            
            return redirect('gestionar_horarios', vet_id=vet_id)
    else:
        form = HorarioMultipleForm()

    horarios_existentes = HorarioDisponible.objects.filter(veterinario=veterinario)
    context = {
        'form': form,
        'veterinario': veterinario,
        'horarios': horarios_existentes
    }
    return render(request, 'core/gestionar_horarios.html', context)

@login_required(login_url='login')
def eliminar_horario(request, pk):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    horario = get_object_or_404(HorarioDisponible, pk=pk)
    vet_id = horario.veterinario.pk
    if request.method == 'POST':
        horario.delete()
        return redirect('gestionar_horarios', vet_id=vet_id)
    context = { 'horario': horario }
    return render(request, 'core/horario_confirmar_eliminar.html', context)

# ============================================================================
# VISTAS: GESTIÓN DE PERSONAL (Solo Admin)
# ============================================================================

@login_required(login_url='login')
def gestionar_personal(request):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    
    personal = Usuario.objects.filter(is_superuser=False).order_by('rol', 'apellido')
    
    # Si es POST, estamos creando o editando
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        if user_id:  # Editar usuario existente
            usuario = get_object_or_404(Usuario, pk=user_id)
            form = PersonalForm(request.POST, instance=usuario)
        else:  # Crear nuevo usuario
            form = PersonalForm(request.POST)
        
        if form.is_valid():
            usuario = form.save()
            
            # Si es veterinario, manejar el perfil extendido
            if usuario.rol == 'VETERINARIO':
                vet_id = request.POST.get('vet_id')
                if vet_id:  # Editar veterinario existente
                    veterinario = get_object_or_404(Veterinario, pk=vet_id)
                    vet_form = VeterinarioForm(request.POST, instance=veterinario)
                else:  # Crear nuevo veterinario
                    vet_form = VeterinarioForm(request.POST)
                
                if vet_form.is_valid():
                    veterinario = vet_form.save(commit=False)
                    veterinario.usuario = usuario
                    veterinario.save()
            
            return redirect('gestionar_personal')
        # Si el formulario no es válido, continuamos para mostrar errores
    
    else:
        # GET request - mostrar formulario vacío o para edición
        user_id = request.GET.get('editar')
        if user_id:
            usuario = get_object_or_404(Usuario, pk=user_id)
            form = PersonalForm(instance=usuario)
            
            # Si es veterinario, cargar datos del perfil extendido
            vet_data = None
            if usuario.rol == 'VETERINARIO' and hasattr(usuario, 'veterinario'):
                vet_data = usuario.veterinario
        else:
            form = PersonalForm()
            vet_data = None
    
    context = {
        'personal': personal,
        'form': form,
        'vet_data': vet_data,
        'editing_user_id': request.GET.get('editar')
    }
    return render(request, 'core/gestionar_personal.html', context)

@login_required(login_url='login')
def eliminar_personal(request, pk):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('gestionar_personal')
    
    return render(request, 'core/personal_confirmar_eliminar.html', {'usuario': usuario})

# ============================================================================
# VISTAS: GESTIÓN DE USUARIOS (Solo Interfaz por ahora)
# ============================================================================

@login_required(login_url='login')
def gestion_usuarios(request):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    usuarios = Usuario.objects.all().order_by('-created_at')
    return render(request, 'core/gestion_usuarios.html', {'usuarios': usuarios})

@login_required(login_url='login')
def crear_usuario(request):
    if request.user.rol != 'ADMIN':
        return redirect('gestion_usuarios')
    # Solo renderiza el formulario, no guarda datos (CRUD no funcional)
    form = PersonalForm()
    return render(request, 'core/usuario_form.html', {'form': form})

@login_required(login_url='login')
def crear_veterinario(request):
    if request.user.rol != 'ADMIN':
        return redirect('gestion_usuarios')
    # Solo renderiza el formulario, no guarda datos (CRUD no funcional)
    form_usuario = PersonalForm(initial={'rol': 'VETERINARIO'})
    form_veterinario = VeterinarioForm()
    context = {
        'form_usuario': form_usuario,
        'form_veterinario': form_veterinario
    }
    return render(request, 'core/veterinario_form.html', context)

# ============================================================================
# VISTAS: CITAS ACTUALES (ADMIN/VETERINARIO)
# ============================================================================

@login_required(login_url='login')
def listar_citas_actuales(request):
    if request.user.rol not in ['ADMIN', 'VETERINARIO']:
        return redirect('panel')
    
    # Mostrar citas de hoy que estén AGENDADAS, CONFIRMADAS o EN_CURSO
    hoy = timezone.localdate()
    citas = Cita.objects.filter(
        fecha_hora__date=hoy,
        estado__in=['AGENDADA', 'CONFIRMADA', 'EN_CURSO']
    ).order_by('fecha_hora')
    
    return render(request, 'core/listar_citas_actuales.html', {'citas': citas, 'hoy': hoy})

@login_required(login_url='login')
def finalizar_cita(request, pk):
    if request.user.rol not in ['ADMIN', 'VETERINARIO']:
        return redirect('panel')
    
    cita = get_object_or_404(Cita, pk=pk)
    
    if request.method == 'POST':
        form = CitaFinalizarForm(request.POST, instance=cita)
        if form.is_valid():
            cita_finalizada = form.save(commit=False)
            cita_finalizada.estado = 'REALIZADO' # Cambiar estado a REALIZADO/FINALIZADA
            cita_finalizada.save()
            return redirect('listar_citas_actuales')
    else:
        form = CitaFinalizarForm(instance=cita)
    
    return render(request, 'core/finalizar_cita_form.html', {'form': form, 'cita': cita})

# ============================================================================
# VISTAS: REPORTES (Solo Admin)
# ============================================================================

@login_required(login_url='login')
def reportes_view(request):
    if request.user.rol != 'ADMIN':
        return redirect('panel')
    
    citas = []
    total_ingresos = 0
    form = ReporteForm(request.GET or None)
    
    if form.is_valid():
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
        paciente = form.cleaned_data['paciente']
        
        # Filtro base: Citas finalizadas en el rango de fechas
        citas = Cita.objects.filter(
            estado='REALIZADO',
            fecha_hora__date__range=[fecha_inicio, fecha_fin]
        )
        
        # Filtro opcional por paciente
        if paciente:
            citas = citas.filter(paciente=paciente)
            
        citas = citas.order_by('fecha_hora')
        
        # Calcular total de ingresos
        total_ingresos = citas.aggregate(Sum('monto'))['monto__sum'] or 0
        
    return render(request, 'core/reportes.html', {
        'form': form,
        'citas': citas,
        'total_ingresos': total_ingresos
    })

    
# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required(login_url='login')
def dashboard_data(request):
    """API endpoint que retorna datos para gráficos del dashboard"""
    from datetime import date
    from dateutil.relativedelta import relativedelta
    
    # Calcular últimos 12 meses
    hoy = date.today()
    primer_mes = hoy - relativedelta(months=11)
    
    # Inicializar datos
    meses_labels = []
    ingresos_data = []
    citas_agendadas = []
    citas_realizadas = []
    citas_canceladas = []
    
    # Generar datos para cada mes
    for i in range(12):
        mes_actual = primer_mes + relativedelta(months=i)
        mes_siguiente = mes_actual + relativedelta(months=1)
        
        # Nombre del mes en español
        meses_esp = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        meses_labels.append(meses_esp[mes_actual.month - 1])
        
        # Ingresos del mes (solo citas REALIZADO)
        ingresos_mes = Cita.objects.filter(
            estado='REALIZADO',
            fecha_hora__gte=mes_actual,
            fecha_hora__lt=mes_siguiente
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        ingresos_data.append(float(ingresos_mes))
        
        # Contar citas por estado
        citas_agendadas.append(Cita.objects.filter(
            estado__in=['SOLICITADA', 'AGENDADA', 'CONFIRMADA'],
            fecha_hora__gte=mes_actual,
            fecha_hora__lt=mes_siguiente
        ).count())
        
        citas_realizadas.append(Cita.objects.filter(
            estado='REALIZADO',
            fecha_hora__gte=mes_actual,
            fecha_hora__lt=mes_siguiente
        ).count())
        
        citas_canceladas.append(Cita.objects.filter(
            estado__in=['CANCELADA', 'NO_ASISTIO'],
            fecha_hora__gte=mes_actual,
            fecha_hora__lt=mes_siguiente
        ).count())
    
    # Retornar JSON
    data = {
        'ingresos_mensuales': {
            'labels': meses_labels,
            'data': ingresos_data
        },
        'citas_por_mes': {
            'labels': meses_labels,
            'agendadas': citas_agendadas,
            'realizadas': citas_realizadas,
            'canceladas': citas_canceladas
        }
    }
    return JsonResponse(data)




# ============================================================================
# VISTAS DE FICHA MÉDICA
# ============================================================================

@login_required(login_url='login')
def ficha_medica_paciente(request, paciente_id):
    """Vista principal de la ficha médica del paciente con pestañas"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Obtener datos para cada sección
    historial = HistorialClinico.objects.filter(paciente=paciente).order_by('-fecha_atencion')
    vacunas = Vacuna.objects.filter(paciente=paciente).order_by('-fecha_aplicacion')
    cirugias = Cirugia.objects.filter(paciente=paciente).order_by('-fecha_cirugia')
    alergias = Alergia.objects.filter(paciente=paciente, activa=True).order_by('-severidad')
    alergias_inactivas = Alergia.objects.filter(paciente=paciente, activa=False).order_by('-fecha_deteccion')
    
    # Verificar vacunas pendientes
    from datetime import date
    vacunas_pendientes = vacunas.filter(proxima_dosis__lte=date.today(), proxima_dosis__isnull=False)
    
    context = {
        'paciente': paciente,
        'historial_consultas': historial,
        'vacunas': vacunas,
        'cirugias': cirugias,
        'alergias': alergias,
        'alergias_inactivas': alergias_inactivas,
        'vacunas_pendientes': vacunas_pendientes,
    }
    
    return render(request, 'core/ficha_medica.html', context)

@login_required(login_url='login')
def agregar_vacuna(request, paciente_id):
    """Vista para agregar un registro de vacuna"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = VacunaForm(request.POST)
        if form.is_valid():
            vacuna = form.save(commit=False)
            vacuna.paciente = paciente
            vacuna.save()
            return redirect('ficha_medica', paciente_id=paciente.id)
    else:
        form = VacunaForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': 'Agregar Vacuna'
    }
    return render(request, 'core/vacuna_form.html', context)

@login_required(login_url='login')
def agregar_cirugia(request, paciente_id):
    """Vista para agregar un registro de cirugía"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = CirugiaForm(request.POST)
        if form.is_valid():
            cirugia = form.save(commit=False)
            cirugia.paciente = paciente
            cirugia.save()
            return redirect('ficha_medica', paciente_id=paciente.id)
    else:
        form = CirugiaForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': 'Agregar Cirugía'
    }
    return render(request, 'core/cirugia_form.html', context)

@login_required(login_url='login')
def agregar_alergia(request, paciente_id):
    """Vista para agregar un registro de alergia/condición"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = AlergiaForm(request.POST)
        if form.is_valid():
            alergia = form.save(commit=False)
            alergia.paciente = paciente
            alergia.save()
            return redirect('ficha_medica', paciente_id=paciente.id)
    else:
        form = AlergiaForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': 'Agregar Alergia/Condición'
    }
    return render(request, 'core/alergia_form.html', context)

@login_required(login_url='login')
def toggle_alergia(request, alergia_id):
    """Vista para activar/desactivar una alergia"""
    alergia = get_object_or_404(Alergia, id=alergia_id)
    alergia.activa = not alergia.activa
    alergia.save()
    return redirect('ficha_medica', paciente_id=alergia.paciente.id)