# core/forms.py

from django import forms
from .models import Cita, Paciente, Veterinario, Tutor, HorarioDisponible, DIA_SEMANA_CHOICES
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
