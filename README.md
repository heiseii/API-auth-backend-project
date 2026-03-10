# 🔐 API de Autenticación y Seguridad

Una API REST backend construida con **Django + Django REST Framework**, enfocada
exclusivamente en seguridad. Implementa autenticación robusta, autorización basada
en roles dinámicos, protección contra ataques de fuerza bruta y rate limiting.

---

## 📋 Tabla de contenidos

- [Características](#-características)
- [Stack tecnológico](#-stack-tecnológico)
- [Arquitectura del proyecto](#-arquitectura-del-proyecto)
- [Endpoints](#-endpoints)
- [Instalación y configuración](#-instalación-y-configuración)
- [Variables de entorno](#-variables-de-entorno)
- [Uso de la API](#-uso-de-la-api)
- [Seguridad](#-seguridad)
- [Documentación interactiva](#-documentación-interactiva)

---

## ✨ Características

| Funcionalidad | Descripción |
|---|---|
| 📝 **Registro** | Creación de usuarios con validación y hashing seguro |
| 🔑 **Login** | Autenticación con email y contraseña |
| 🔒 **Hashing con bcrypt** | Contraseñas protegidas con BCryptSHA256 |
| 🎟️ **JWT + Refresh Tokens** | Tokens de acceso de corta duración con renovación automática |
| 🚫 **Revocación de tokens** | Logout real mediante blacklist de tokens |
| 🛡️ **Middleware de autorización** | Verificación automática de permisos en cada request |
| 👥 **Roles y permisos dinámicos** | Sistema de roles y permisos configurables desde la base de datos |
| ⏱️ **Rate limiting** | Límite de requests por IP y por usuario |
| 🔐 **Bloqueo por intentos fallidos** | Bloquea usuarios tras múltiples fallos de login |

---

## 🛠 Stack tecnológico

- **Lenguaje:** Python 3.11+
- **Framework:** Django 5 + Django REST Framework
- **Base de datos:** PostgreSQL
- **Autenticación:** djangorestframework-simplejwt
- **Hashing:** BCryptSHA256 (django-bcrypt)
- **Rate limiting:** DRF Throttling
- **Documentación:** drf-spectacular (OpenAPI/Swagger)
- **Configuración:** python-decouple

---

## 🗂 Arquitectura del proyecto
```
api_auth/
├── manage.py
├── requirements.txt
├── .env                          # Variables de entorno (no subir a Git)
├── .env.example                  # Ejemplo de variables de entorno
├── config/
│   ├── settings.py               # Configuración global
│   ├── urls.py                   # Rutas principales
│   └── wsgi.py
└── apps/
    ├── users/
    │   ├── models.py             # CustomUser, Role, Permission
    │   ├── serializers.py        # Validación y serialización de datos
    │   ├── views.py              # Registro, perfil de usuario
    │   └── urls.py
    └── authentication/
        ├── views.py              # Login, Logout, Refresh, Revocación
        ├── serializers.py        # CustomTokenObtainPairSerializer
        ├── urls.py
        ├── middleware.py         # Middleware de autorización JWT
        └── throttles.py          # Rate limiting personalizado
```

---

## 🌐 Endpoints

### Autenticación

| Método | Endpoint | Descripción | Auth requerida |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Registro de nuevo usuario | ❌ |
| `POST` | `/api/auth/login/` | Login, retorna access + refresh token | ❌ |
| `POST` | `/api/auth/logout/` | Revoca el refresh token (blacklist) | ✅ |
| `POST` | `/api/auth/token/refresh/` | Obtiene nuevo access token | ✅ Refresh token |

### Usuarios

| Método | Endpoint | Descripción | Auth requerida |
|---|---|---|---|
| `GET` | `/api/users/me/` | Perfil del usuario autenticado | ✅ |
| `PUT` | `/api/users/me/` | Actualizar perfil propio | ✅ |
| `GET` | `/api/users/` | Listar usuarios | ✅ Admin |

### Roles y Permisos

| Método | Endpoint | Descripción | Auth requerida |
|---|---|---|---|
| `GET` | `/api/users/roles/` | Listar roles disponibles | ✅ Admin |
| `POST` | `/api/users/roles/` | Crear nuevo rol | ✅ Admin |
| `POST` | `/api/users/roles/{id}/assign/` | Asignar rol a usuario | ✅ Admin |

---

## 🚀 Instalación y configuración

### Prerrequisitos

- Python 3.11+
- PostgreSQL
- pip

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/API-auth-backend-project.git
cd API-auth-backend-project
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv venv

# Linux/Mac — bash/zsh
source venv/bin/activate

# Linux/Mac — Fish shell
source venv/bin/activate.fish

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editá el .env con tus valores
```

### 5. Crear la base de datos en PostgreSQL
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE api_auth_db;
CREATE USER api_auth_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE api_auth_db TO api_auth_user;
\q
```

### 6. Aplicar migraciones
```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor
```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000`

---

## ⚙️ Variables de entorno

Copiá `.env.example` a `.env` y completá los valores:
```env
# Django
SECRET_KEY=cambia-esto-por-una-clave-secreta-larga-y-aleatoria
DEBUG=True

# Base de datos
DB_NAME=api_auth_db
DB_USER=api_auth_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# JWT
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7

# Seguridad
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

> ⚠️ **Nunca subas el archivo `.env` a Git.** Asegurate de tenerlo en tu `.gitignore`.

---

## 📖 Uso de la API

### Registro
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario",
    "password": "contraseña_segura123",
    "password_confirm": "contraseña_segura123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "contraseña_segura123"
  }'
```

**Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "usuario",
    "roles": ["user"]
  }
}
```

### Usar el access token
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Logout (revocación de token)
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

## 🔐 Seguridad

### Hashing de contraseñas
Las contraseñas se hashean con **BCryptSHA256**. Django nunca almacena contraseñas en texto plano.

### JWT — Access y Refresh Tokens
- El **access token** expira en **15 minutos** por defecto.
- El **refresh token** expira en **7 días** por defecto.
- Cada vez que se usa el refresh token, se emite uno nuevo y el anterior queda **revocado automáticamente**.

### Bloqueo por intentos fallidos
Tras **5 intentos fallidos** de login (configurable), la cuenta queda bloqueada por **15 minutos**. Previene ataques de fuerza bruta.

### Rate Limiting

| Tipo | Límite |
|---|---|
| Usuarios anónimos | 100 requests / día |
| Usuarios autenticados | 1000 requests / día |
| Endpoint de login | 5 requests / minuto |

### Roles y permisos dinámicos
Los roles y permisos se gestionan desde la base de datos, sin necesidad de modificar código para configurar accesos.

---

## 📚 Documentación interactiva

Con el servidor corriendo, accedé a Swagger en:
```
http://localhost:8000/api/docs/
```

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.
