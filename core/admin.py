# core/admin.py

from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import (
    Usuario, Veterinario, Tutor, Paciente,
    Cita, HistorialClinico, HorarioDisponible,
    Vacuna, Cirugia, Alergia
)

# ===============================================================
# FORMULARIOS PERSONALIZADOS PARA USUARIO
# (Esta es la lógica que faltaba porque el archivo estaba roto)
# ===============================================================

class CustomUserCreationForm(forms.ModelForm):
    """Formulario para crear usuarios en el admin"""
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido', 'rol')

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # Asignamos campos extra que el form por defecto no tiene
        user.is_staff = False 
        user.is_superuser = False
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    """Formulario para editar usuarios en el admin"""
    password = ReadOnlyPasswordHashField(
        help_text=('Las contraseñas encriptadas no se guardan aquí. '
                   'Usa <a href="password/">este formulario</a> para cambiarla.')
    )

    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'apellido', 'rol', 'password', 'is_active', 'is_staff', 'is_superuser')

# ===============================================================
# CONFIGURACIÓN DEL ADMIN
# ===============================================================

class CustomUserAdmin(UserAdmin):
    # Le decimos a Django que use nuestros formularios personalizados
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Usuario
    list_display = ('email', 'nombre', 'apellido', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff', 'is_active')

    # Campos al MODIFICAR un usuario
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Fechas importantes', {'fields': ('last_login',)}),
    )

    # Campos al AÑADIR un usuario (este es el que estabas usando)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Usamos los campos de nuestro CustomUserCreationForm
            'fields': ('email', 'nombre', 'apellido', 'rol', 'password', 'password2'),
        }),
    )

    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)


# ===============================================================
# REGISTRO DE MODELOS
# ===============================================================

# Quitamos el registro por defecto y usamos el nuestro
try:
    admin.site.unregister(Usuario)
except admin.sites.NotRegistered:
    pass
admin.site.register(Usuario, CustomUserAdmin)


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rut', 'especialidad', 'telefono')
    search_fields = ('usuario__nombre', 'usuario__apellido', 'rut')

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rut', 'telefono', 'email')
    search_fields = ('nombre', 'apellido', 'rut')

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'tutor', 'activo')
    list_filter = ('especie', 'sexo', 'activo')
    search_fields = ('nombre', 'tutor__nombre', 'tutor__apellido')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'veterinario', 'fecha_hora', 'estado')
    list_filter = ('estado', 'veterinario')
    search_fields = ('paciente__nombre', 'veterinario__usuario__nombre')

@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'veterinario', 'fecha_atencion')
    search_fields = ('paciente__nombre', 'veterinario__usuario__nombre')

@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('veterinario', 'get_dia_semana_display', 'hora_inicio', 'hora_fin')
    list_filter = ('veterinario', 'dia_semana')

@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'nombre_vacuna', 'fecha_aplicacion', 'proxima_dosis', 'veterinario')
    list_filter = ('nombre_vacuna', 'fecha_aplicacion')
    search_fields = ('paciente__nombre', 'nombre_vacuna')
    date_hierarchy = 'fecha_aplicacion'

@admin.register(Cirugia)
class CirugiaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo_cirugia', 'fecha_cirugia', 'veterinario', 'costo')
    list_filter = ('tipo_cirugia', 'fecha_cirugia')
    search_fields = ('paciente__nombre', 'tipo_cirugia')
    date_hierarchy = 'fecha_cirugia'

@admin.register(Alergia)
class AlergiaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo', 'descripcion', 'severidad', 'activa')
    list_filter = ('tipo', 'severidad', 'activa')
    search_fields = ('paciente__nombre', 'descripcion')
