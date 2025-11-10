# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse 
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST

# Importamos todos los Modelos y Forms que usaremos
from .models import Usuario, Cita, Tutor, Paciente, Veterinario, HorarioDisponible
from .forms import CitaForm, TutorForm, PacienteForm, HorarioForm, PersonalForm, VeterinarioForm

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
        # Estadísticas para el dashboard
        total_pacientes = Paciente.objects.count()
        total_veterinarios = Veterinario.objects.count()
        citas_pendientes = Cita.objects.filter(
            estado__in=['SOLICITADA', 'AGENDADA']
        ).count()
        citas_hoy = Cita.objects.filter(
            fecha_hora__date=timezone.localdate()
        ).count()
        
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
        form = HorarioForm(request.POST)
        if form.is_valid():
            try:
                horario = form.save(commit=False)
                horario.veterinario = veterinario 
                horario.clean() 
                horario.save()
                return redirect('gestionar_horarios', vet_id=vet_id)
            except ValidationError as e:
                form.add_error(None, e)
    else:
        form = HorarioForm()

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