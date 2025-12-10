# core/forms.py

from django import forms
from .models import (
    Cita, Paciente, Veterinario, Tutor, HorarioDisponible,
    DIA_SEMANA_CHOICES, Usuario  # 👈 Se agregó Usuario aquí
)
from django.core.exceptions import ValidationError
from django.utils import timezone

# --- Formulario de Cita (Versión ÚNICA con validación) ---
class CitaForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        label="Paciente",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    veterinario = forms.ModelChoiceField(
        queryset=Veterinario.objects.all(),
        label="Veterinario",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Cita
        fields = ['paciente', 'veterinario', 'fecha_hora', 'motivo_consulta']
        widgets = {
            'fecha_hora': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'motivo_consulta': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
        }
        labels = {
            'fecha_hora': 'Fecha y Hora',
            'motivo_consulta': 'Motivo de la Consulta',
        }
    
    def __init__(self, *args, **kwargs):
        super(CitaForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.fecha_hora:
            self.initial['fecha_hora'] = self.instance.fecha_hora.strftime('%Y-%m-%dT%H:%M')

    # --- LÓGICA DE VALIDACIÓN DE HORARIO ---
    def clean(self):
        cleaned_data = super().clean()
        fecha_hora = cleaned_data.get("fecha_hora")
        veterinario = cleaned_data.get("veterinario")

        if not fecha_hora or not veterinario:
            return cleaned_data

        if fecha_hora < timezone.now():
            raise ValidationError("No se puede agendar una cita en una fecha u hora pasada.")

        dia_semana = fecha_hora.weekday()
        hora_cita = fecha_hora.time()
        
        horarios_vet = HorarioDisponible.objects.filter(
            veterinario=veterinario, 
            dia_semana=dia_semana
        )
        
        if not horarios_vet.exists():
            raise ValidationError(f"El veterinario seleccionado no trabaja el día {fecha_hora.strftime('%A')}.")

        disponible_en_horario = False
        for bloque in horarios_vet:
            if bloque.hora_inicio <= hora_cita < bloque.hora_fin:
                disponible_en_horario = True
                break
        
        if not disponible_en_horario:
            raise ValidationError("La hora seleccionada está fuera del horario laboral del veterinario.")

        citas_existentes = Cita.objects.filter(
            veterinario=veterinario,
            fecha_hora=fecha_hora
        )
        
        if self.instance.pk:
            citas_existentes = citas_existentes.exclude(pk=self.instance.pk)
        
        if citas_existentes.exists():
            raise ValidationError("El veterinario ya tiene una cita agendada a esta misma hora.")

        return cleaned_data


# --- Formulario de Tutor (Versión ÚNICA) ---
class TutorForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = ['nombre', 'apellido', 'rut', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# --- Formulario de Paciente (Versión ÚNICA) ---
class PacienteForm(forms.ModelForm):
    tutor = forms.ModelChoiceField(
        queryset=Tutor.objects.all(),
        label="Tutor",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Paciente
        fields = [
            'tutor', 'nombre', 'especie', 'raza', 'sexo', 
            'fecha_nacimiento', 'color', 'peso', 'observaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'especie': forms.Select(attrs={'class': 'form-select'}),
            'raza': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_nacimiento': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'peso': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'observaciones': 'Observaciones (Alergias, etc.)',
        }
    
    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.fecha_nacimiento:
            self.initial['fecha_nacimiento'] = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')


# --- NUEVO FORMULARIO: HorarioDisponible ---
class HorarioForm(forms.ModelForm):
    dia_semana = forms.ChoiceField(
        choices=DIA_SEMANA_CHOICES,
        label="Día de la semana",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    hora_inicio = forms.TimeField(
        label="Hora de Inicio",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    hora_fin = forms.TimeField(
        label="Hora de Fin",
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    class Meta:
        model = HorarioDisponible
        fields = ['dia_semana', 'hora_inicio', 'hora_fin']


# --- Formulario para Personal ---
class PersonalForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        required=False
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        required=False
    )
    
    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'apellido', 'rol', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@clinica.com'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Usuario Activo'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        
        if password or password2:
            if password != password2:
                raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


# --- Formulario para Veterinario ---
class VeterinarioForm(forms.ModelForm):
    class Meta:
        model = Veterinario
        fields = ['rut', 'especialidad', 'telefono']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345678-9'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cirugía, Medicina Interna, etc.'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'}),
        }


# --- Formulario para Finalizar Cita (Veterinario/Admin) ---
class CitaFinalizarForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['monto', 'tipo_pago', 'observaciones_veterinario']
        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 25000'}),
            'tipo_pago': forms.Select(attrs={'class': 'form-select'}),
            'observaciones_veterinario': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Diagnóstico, tratamiento, etc.'}),
        }
        labels = {
            'observaciones_veterinario': 'Observaciones y Diagnóstico'
        }
    
    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if not monto:
            raise ValidationError("Debe ingresar el monto de la consulta.")
        if monto < 0:
            raise ValidationError("El monto no puede ser negativo.")
        return monto

    def clean_tipo_pago(self):
        tipo_pago = self.cleaned_data.get('tipo_pago')
        if not tipo_pago:
            raise ValidationError("Debe seleccionar un tipo de pago.")
        return tipo_pago


# --- Formulario de Reportes ---
class ReporteForm(forms.Form):
    fecha_inicio = forms.DateField(
        label="Fecha Inicio",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    fecha_fin = forms.DateField(
        label="Fecha Fin",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        label="Filtrar por Paciente (Opcional)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# ============================================================================
# FORMS PARA FICHA MÉDICA
# ============================================================================

from .models import Vacuna, Cirugia, Alergia

class VacunaForm(forms.ModelForm):
    class Meta:
        model = Vacuna
        fields = ['nombre_vacuna', 'fecha_aplicacion', 'proxima_dosis', 'lote', 'veterinario', 'observaciones']
        widgets = {
            'nombre_vacuna': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_aplicacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proxima_dosis': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CirugiaForm(forms.ModelForm):
    class Meta:
        model = Cirugia
        fields = ['tipo_cirugia', 'fecha_cirugia', 'veterinario', 'descripcion', 'complicaciones', 'costo']
        widgets = {
            'tipo_cirugia': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_cirugia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'veterinario': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'complicaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'costo': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AlergiaForm(forms.ModelForm):
    class Meta:
        model = Alergia
        fields = ['tipo', 'descripcion', 'severidad', 'fecha_deteccion', 'activa', 'observaciones']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'severidad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_deteccion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

        

class HorarioMultipleForm(forms.Form):
    """Formulario para crear horarios en múltiples días a la vez"""
    dias_semana = forms.MultipleChoiceField(
        choices=(
            (0, 'Lunes'),
            (1, 'Martes'),
            (2, 'Miércoles'),
            (3, 'Jueves'),
            (4, 'Viernes'),
            (5, 'Sábado'),
            (6, 'Domingo'),
        ),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Días de la semana',
        required=True
    )
    hora_inicio = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label='Hora de inicio'
    )
    hora_fin = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label='Hora de fin'
    )

    

# ============================================================================
# FORMULARIOS: PAGOS Y GESTIÓN DE CITAS
# ============================================================================

class CitaFinalizarForm(forms.Form):
    """Formulario para finalizar una cita y registrar pago"""
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        label='Monto Total'
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Observaciones Clínicas',
        required=False
    )
    pago_inmediato = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='¿El cliente pagó hoy?'
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('EFECTIVO', 'Efectivo'),
            ('DEBITO', 'Débito'),
            ('CREDITO', 'Crédito'),
            ('TRANSFERENCIA', 'Transferencia'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Método de Pago',
        required=False
    )

class CancelarCitaForm(forms.Form):
    """Formulario para cancelar una cita"""
    motivo_cancelacion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Motivo de Cancelación'
    )

class AbonoForm(forms.Form):
    """Formulario para registrar un abono/pago parcial"""
    monto = forms.DecimalField(
        max_digits=10,
        decimal_places=0,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Monto del Abono'
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('EFECTIVO', 'Efectivo'),
            ('DEBITO', 'Débito'),
            ('CREDITO', 'Crédito'),
            ('TRANSFERENCIA', 'Transferencia'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Método de Pago'
    )
    notas = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label='Notas',
        required=False
    )