
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