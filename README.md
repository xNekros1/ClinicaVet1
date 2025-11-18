# ClínicaVet+ - Sistema de Gestión para Clínica Veterinaria

Sistema web desarrollado en Django para la gestión integral de una clínica veterinaria. Incluye gestión de citas, pacientes, tutores, personal, horarios y historial clínico.

## 🚀 Características

- **Gestión de Citas**: Agendamiento, confirmación y seguimiento de citas médicas
- **Gestión de Pacientes**: Registro completo de mascotas con información detallada
- **Gestión de Tutores**: Administración de dueños de mascotas
- **Historial Clínico**: Registro completo de atenciones médicas
- **Gestión de Personal**: Administración de usuarios del sistema (Administradores, Veterinarios, Recepcionistas)
- **Horarios de Veterinarios**: Configuración de disponibilidad de veterinarios
- **Sistema de Roles**: Control de acceso basado en roles (ADMIN, VETERINARIO, RECEPCIONISTA)
- **Búsqueda y Paginación**: Búsqueda avanzada y paginación en todos los listados
- **Interfaz Responsive**: Diseño moderno y adaptable a diferentes dispositivos
- **Tema Claro/Oscuro**: Soporte para modo claro y oscuro

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- PostgreSQL (para producción) o SQLite (para desarrollo)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ClinicaVet-master
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
SECRET_KEY=tu-secret-key-aqui-genera-una-nueva
DEBUG=True
DATABASE_URL=
RENDER_EXTERNAL_HOSTNAME=
```

**Nota**: Para generar una nueva SECRET_KEY, puedes usar:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5. Configurar base de datos

#### Para desarrollo (SQLite):
Si no defines `DATABASE_URL`, el sistema usará SQLite automáticamente.

#### Para producción (PostgreSQL):
Define `DATABASE_URL` con la URL de conexión a tu base de datos PostgreSQL:
```env
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/nombre_bd
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear el primer usuario administrador.

### 8. Recopilar archivos estáticos (solo para producción)

```bash
python manage.py collectstatic --noinput
```

### 9. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en `http://localhost:8000`

## 👥 Roles del Sistema

### Administrador (ADMIN)
- Acceso completo al sistema
- Gestión de personal
- Gestión de horarios de veterinarios
- Acceso a reportes
- CRUD completo de todas las entidades

### Veterinario (VETERINARIO)
- Ver y crear historiales clínicos
- Ver agenda de citas
- Ver pacientes
- Crear citas (estado: SOLICITADA)

### Recepcionista (RECEPCIONISTA)
- Gestión de citas (crear, editar, eliminar, confirmar)
- Gestión de pacientes
- Gestión de tutores
- Ver agenda

## 📁 Estructura del Proyecto

```
ClinicaVet-master/
├── clinica_veterinaria/    # Configuración principal Django
│   ├── settings.py         # Configuración del proyecto
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuración WSGI
├── core/                   # Aplicación principal
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas y lógica de negocio
│   ├── forms.py            # Formularios
│   ├── admin.py            # Configuración del admin
│   ├── tests.py            # Tests unitarios
│   └── migrations/         # Migraciones de BD
├── templates/              # Plantillas HTML
│   └── core/               # Templates de la app core
├── static/                 # Archivos estáticos
│   ├── css/               # Estilos CSS
│   ├── js/                # JavaScript
│   └── img/               # Imágenes
├── requirements.txt        # Dependencias Python
├── manage.py              # Script de gestión Django
└── README.md              # Este archivo
```

## 🧪 Ejecutar Tests

```bash
python manage.py test
```

## 🚢 Despliegue en Producción

### Render.com

1. Conecta tu repositorio a Render
2. Configura las variables de entorno en el dashboard de Render:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `DEBUG=False`
   - `RENDER_EXTERNAL_HOSTNAME` (se configura automáticamente)
3. El sistema detectará automáticamente el entorno de Render

### Otras plataformas

Asegúrate de configurar:
- Variables de entorno correctamente
- Base de datos PostgreSQL
- Archivos estáticos (usando WhiteNoise)
- `ALLOWED_HOSTS` en settings.py

## 🔒 Seguridad

- **SECRET_KEY**: Nunca commitees la SECRET_KEY en el código. Usa variables de entorno.
- **Credenciales de BD**: Mantén las credenciales de base de datos en variables de entorno.
- **DEBUG**: Siempre establece `DEBUG=False` en producción.

## 📝 Notas Adicionales

- El sistema usa zona horaria `America/Santiago` (Chile)
- Idioma configurado: Español de Chile (`es-cl`)
- Los archivos estáticos se sirven con WhiteNoise en producción

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de uso privado.

## 👨‍💻 Autor

Desarrollado para gestión de clínica veterinaria.

---

**Versión**: 1.0.0  
**Última actualización**: 2025

