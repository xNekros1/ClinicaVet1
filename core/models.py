# core/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
import datetime

# ============================================================================
# CHOICES
# ============================================================================

rol_choices = [
    ("ADMIN", "Administrador"),
    ("VETERINARIO", "Veterinario"),
    ("RECEPCIONISTA", "Recepcionista"),
]
especie_choices = [
    ("CANINO", "Perro"),
    ("FELINO", "Gato"),
    ("AVE", "Ave"),
    ("ROEDOR", "Roedor"),
    ("REPTIL", "Reptil"),
    ("OTRO", "Otro"),
]
sexo_choices = [
    ("M", "Macho"),
    ("H", "Hembra"),
]
estado_cita_choices = [
    ("SOLICITADA", "Solicitada por Veterinario"),
    ("AGENDADA", "Agendada"),
    ("CONFIRMADA", "Confirmada"),
    ("EN_CURSO", "En Curso"),
    ("REALIZADO", "Realizado"),
    ("CANCELADA", "Cancelada"),
    ("NO_ASISTIO", "No Asistió"),
]
DIA_SEMANA_CHOICES = [
    (0, "Lunes"),
    (1, "Martes"),
    (2, "Miércoles"),
    (3, "Jueves"),
    (4, "Viernes"),
    (5, "Sábado"),
    (6, "Domingo"),
]

# ============================================================================
# MANAGER PARA USUARIO
# ============================================================================

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# ============================================================================
# MODELO USUARIO
# ============================================================================

class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, help_text="Correo electrónico del usuario")
    nombre = models.CharField(max_length=100, help_text="Nombre del usuario")
    apellido = models.CharField(max_length=100, help_text="Apellido del usuario")
    rol = models.CharField(
        max_length=20, 
        choices=rol_choices, 
        default="RECEPCIONISTA",
        help_text="Rol del usuario en el sistema"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    objects = UsuarioManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"

# ============================================================================
# MODELO VETERINARIO
# ============================================================================

class Veterinario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, help_text="Usuario asociado al veterinario")
    rut = models.CharField(max_length=12, unique=True, help_text="RUT sin puntos, con guión. Ej: 12345678-9")
    especialidad = models.CharField(max_length=100, blank=True, help_text="Especialidad del veterinario. Ej: Cirugía, Medicina Interna")
    telefono = models.CharField(max_length=15, help_text="Teléfono del veterinario. Ej: +56912345678")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Dr(a). {self.usuario.nombre} {self.usuario.apellido}"

# ============================================================================
# MODELO TUTOR
# ============================================================================

class Tutor(models.Model):
    nombre = models.CharField(max_length=100, help_text="Nombre del tutor (dueño)")
    apellido = models.CharField(max_length=100, help_text="Apellido del tutor")
    rut = models.CharField(max_length=12, unique=True, help_text="RUT sin puntos, con guión. Ej: 12345678-9")
    telefono = models.CharField(max_length=15, help_text="Teléfono de contacto")
    email = models.EmailField(blank=True, null=True, help_text="Correo electrónico (opcional)")
    direccion = models.TextField(blank=True, help_text="Dirección del tutor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# ============================================================================
# MODELO PACIENTE (MASCOTA)
# ============================================================================

class Paciente(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, help_text="Tutor (dueño) de la mascota")
    nombre = models.CharField(max_length=100, help_text="Nombre de la mascota")
    especie = models.CharField(max_length=20, choices=especie_choices, help_text="Especie de la mascota")
    raza = models.CharField(max_length=100, blank=True, help_text="Raza de la mascota (opcional)")
    sexo = models.CharField(max_length=1, choices=sexo_choices, default="M", help_text="Sexo de la mascota")
    fecha_nacimiento = models.DateField(null=True, blank=True, help_text="Fecha de nacimiento de la mascota")
    color = models.CharField(max_length=50, blank=True, help_text="Color de la mascota")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Peso en kilogramos")
    observaciones = models.TextField(blank=True, help_text="Observaciones generales (alergias, condiciones especiales, etc.)")
    activo = models.BooleanField(default=True, help_text="Indica si el paciente está activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nombre} ({self.especie}) - Tutor: {self.tutor.nombre}"

# ============================================================================
# MODELO CITA
# ============================================================================

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, help_text="Mascota que será atendida")
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT, help_text="Veterinario que atenderá la cita")
    fecha_hora = models.DateTimeField(help_text="Fecha y hora de la cita")
    motivo_consulta = models.TextField(help_text="Motivo de la consulta")
    estado = models.CharField(
        max_length=20, 
        choices=estado_cita_choices, 
        default="AGENDADA",
        help_text="Estado actual de la cita"
    )
    notas_recepcion = models.TextField(blank=True, help_text="Notas adicionales del recepcionista")
    creada_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="citas_creadas"
    )
    
    # Campos para finalización de cita (Veterinario)
    monto = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, help_text="Monto total de la consulta")
    tipo_pago = models.CharField(
        max_length=20,
        choices=[
            ('DEBITO', 'Débito'),
            ('CREDITO', 'Crédito'),
            ('EFECTIVO', 'Efectivo')
        ],
        null=True,
        blank=True,
        help_text="Tipo de pago realizado"
    )
    observaciones_veterinario = models.TextField(blank=True, help_text="Observaciones y resumen de la atención por parte del veterinario")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Cita: {self.paciente.nombre} - {self.fecha_hora} ({self.estado})"

# ============================================================================
# MODELO HISTORIAL CLINICO
# ============================================================================
class HistorialClinico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, help_text="Mascota del historial")
    cita = models.OneToOneField(Cita, on_delete=models.SET_NULL, null=True, blank=True, help_text="Cita asociada (opcional)")
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT, help_text="Veterinario que realizó la atención")
    fecha_atencion = models.DateTimeField(help_text="Fecha y hora de la atención")
    motivo = models.TextField(help_text="Motivo de la consulta")
    diagnostico = models.TextField(help_text="Diagnóstico médico")
    tratamiento = models.TextField(help_text="Tratamiento prescrito")
    notas = models.TextField(blank=True, help_text="Notas adicionales del veterinario")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Historial: {self.paciente.nombre} - {self.fecha_atencion}"

# ============================================================================
# MODELO: HORARIO DISPONIBLE
# ============================================================================
class HorarioDisponible(models.Model):
    veterinario = models.ForeignKey(
        Veterinario, 
        on_delete=models.CASCADE, 
        related_name="horarios",
        help_text="Veterinario al que pertenece este bloque de horario"
    )
    dia_semana = models.IntegerField(
        choices=DIA_SEMANA_CHOICES,
        help_text="Día de la semana para este bloque"
    )
    hora_inicio = models.TimeField(help_text="Hora de inicio del bloque")
    hora_fin = models.TimeField(help_text="Hora de fin del bloque")

    class Meta:
        unique_together = ('veterinario', 'dia_semana', 'hora_inicio', 'hora_fin')
        ordering = ['veterinario', 'dia_semana', 'hora_inicio']

    def __str__(self):
        return f"{self.veterinario} - {self.get_dia_semana_display()}: {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")
        
        if not hasattr(self, 'veterinario') or not self.veterinario:
             return 

        horarios_existentes = HorarioDisponible.objects.filter(
            veterinario=self.veterinario,
            dia_semana=self.dia_semana
        ).exclude(pk=self.pk)

        for horario in horarios_existentes:
            if max(self.hora_inicio, horario.hora_inicio) < min(self.hora_fin, horario.hora_fin):
                raise ValidationError(f"Este horario se solapa con un bloque existente ({horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}).")

# ============================================================================
# MODELO: VACUNA
# ============================================================================
class Vacuna(models.Model):
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        related_name="vacunas",
        help_text="Mascota vacunada"
    )
    nombre_vacuna = models.CharField(
        max_length=100, 
        help_text="Nombre de la vacuna (ej: Rabia, Parvovirus, Triple Felina)"
    )
    fecha_aplicacion = models.DateField(help_text="Fecha en que se aplicó la vacuna")
    proxima_dosis = models.DateField(
        null=True, 
        blank=True, 
        help_text="Fecha programada para la próxima dosis (si aplica)"
    )
    lote = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Número de lote de la vacuna"
    )
    veterinario = models.ForeignKey(
        Veterinario, 
        on_delete=models.PROTECT, 
        help_text="Veterinario que aplicó la vacuna"
    )
    observaciones = models.TextField(
        blank=True, 
        help_text="Observaciones adicionales sobre la vacunación"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_aplicacion']
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"

    def __str__(self):
        return f"{self.nombre_vacuna} - {self.paciente.nombre} ({self.fecha_aplicacion})"

# ============================================================================
# MODELO: CIRUGIA
# ============================================================================
class Cirugia(models.Model):
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        related_name="cirugias",
        help_text="Mascota operada"
    )
    tipo_cirugia = models.CharField(
        max_length=150, 
        help_text="Tipo de cirugía (ej: Esterilización, Extracción dental, Cesárea)"
    )
    fecha_cirugia = models.DateField(help_text="Fecha en que se realizó la cirugía")
    veterinario = models.ForeignKey(
        Veterinario, 
        on_delete=models.PROTECT, 
        help_text="Veterinario que realizó la cirugía"
    )
    descripcion = models.TextField(help_text="Descripción detallada del procedimiento")
    complicaciones = models.TextField(
        blank=True, 
        help_text="Complicaciones observadas durante o después de la cirugía"
    )
    costo = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        help_text="Costo de la cirugía"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_cirugia']
        verbose_name = "Cirugía"
        verbose_name_plural = "Cirugías"

    def __str__(self):
        return f"{self.tipo_cirugia} - {self.paciente.nombre} ({self.fecha_cirugia})"

# ============================================================================
# MODELO: ALERGIA/CONDICION
# ============================================================================
class Alergia(models.Model):
    TIPO_CHOICES = [
        ('ALERGIA', 'Alergia'),
        ('CONDICION_CRONICA', 'Condición Crónica'),
        ('MEDICAMENTO_PROHIBIDO', 'Medicamento Prohibido'),
        ('OTRO', 'Otro'),
    ]
    SEVERIDAD_CHOICES = [
        ('LEVE', 'Leve'),
        ('MODERADA', 'Moderada'),
        ('GRAVE', 'Grave'),
    ]

    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        related_name="alergias",
        help_text="Mascota con la condición/alergia"
    )
    tipo = models.CharField(
        max_length=30, 
        choices=TIPO_CHOICES, 
        default='ALERGIA',
        help_text="Tipo de condición"
    )
    descripcion = models.TextField(
        help_text="Descripción detallada de la alergia o condición"
    )
    severidad = models.CharField(
        max_length=15, 
        choices=SEVERIDAD_CHOICES, 
        default='MODERADA',
        help_text="Nivel de severidad"
    )
    fecha_deteccion = models.DateField(
        help_text="Fecha en que se detectó la condición"
    )
    activa = models.BooleanField(
        default=True, 
        help_text="Indica si la condición sigue activa"
    )
    observaciones = models.TextField(
        blank=True, 
        help_text="Observaciones adicionales"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-activa', '-severidad', '-fecha_deteccion']
        verbose_name = "Alergia/Condición"
        verbose_name_plural = "Alergias/Condiciones"

    def __str__(self):
        estado = "Activa" if self.activa else "Inactiva"
        return f"{self.get_tipo_display()} - {self.paciente.nombre} ({estado})"
