# Sistema de Gestión de Biblioteca Digital (Microservicios)

Arquitectura desacoplada basada en tres servicios integrados dentro de una misma red virtual (`bridge`):

```
Cliente ──► API Gateway (:8080) ──► Servicio de Libros (FastAPI, :8000) ──► Base de Datos (PostgreSQL)
```

| Componente | Stack | Rol principal |
| --- | --- | --- |
| **Gateway** | FastAPI + `httpx` | Entrada centralizada. Maneja validación de tokens JWT, límite de peticiones (rate limiting), políticas CORS y trazabilidad mediante `X-Request-ID`. |
| **Servicio de Libros** | FastAPI + SQLAlchemy | Administración de catálogos e inscritos (CRUD de libros y socios) aplicando arquitectura por capas (DTOs, Repositorios e Inyección de Dependencias). |
| **Base de Datos** | PostgreSQL 16 | Almacenamiento persistente mediante el volumen montado `pgdata`. |

Solo el Gateway publica un puerto hacia el exterior (8080). El servicio de libros y la base de datos son accesibles únicamente dentro de la red `biblioteca-net`.

---

## Pre-requisitos

* Tener instalados **Docker** y **Docker Compose** (con Docker Desktop abierto si usas Windows o macOS).
* Editor recomendado: Visual Studio Code.
* Opcional para probar la API: Postman.

---

## Puesta en marcha rápida

1. **Clonar el repositorio y preparar las variables:**

```bash
git clone <URL-DEL-REPOSITORIO>
cd biblioteca-microservicios
cp .env.example .env
```

En PowerShell, el último comando es `Copy-Item .env.example .env`. Este paso es opcional: el proyecto tiene valores por defecto.

2. **Levantar el entorno con Docker** (desde la carpeta que contiene `docker-compose.yml`):

```bash
docker-compose up --build
```

El Gateway responderá en `http://localhost:8080`. Para dejarlo en segundo plano usa `docker-compose up -d --build` y comprueba el estado con `docker-compose ps`: los tres servicios deben aparecer como `healthy`.

3. **Para detener los contenedores:**

```bash
docker-compose down
```

Agrega la bandera `-v` si deseas borrar también el volumen de datos.

---

## Ejemplos de uso con cURL (Linux, macOS, Git Bash)

### 1. Estado del servicio

```bash
curl http://localhost:8080/health
```

### 2. Autenticación

Credenciales de prueba: usuario `admin` / contraseña `admin123`.

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

> **Tip:** guarda el token en una variable para los siguientes pasos:
> `TOKEN="<tu_access_token>"`

### 3. Gestión del catálogo de libros

* **Registrar libro:**

```bash
curl -X POST http://localhost:8080/api/books \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cien años de soledad",
    "author": "Gabriel García Márquez",
    "isbn": "9780307474728",
    "year": 1967,
    "copies_available": 3
  }'
```

* **Consultar inventario:**

```bash
curl http://localhost:8080/api/books -H "Authorization: Bearer $TOKEN"
```

* **Buscar por ID:**

```bash
curl http://localhost:8080/api/books/1 -H "Authorization: Bearer $TOKEN"
```

* **Modificar un libro:**

```bash
curl -X PUT http://localhost:8080/api/books/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cien años de soledad",
    "author": "Gabriel García Márquez",
    "isbn": "9780307474728",
    "year": 1967,
    "copies_available": 5
  }'
```

* **Dar de baja un libro:**

```bash
curl -X DELETE http://localhost:8080/api/books/1 -H "Authorization: Bearer $TOKEN"
```

### 4. Registro de socios

* **Dar de alta un socio:**

```bash
curl -X POST http://localhost:8080/api/members \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Brayan Chambi", "email": "brayan@example.com"}'
```

* **Listar socios:**

```bash
curl http://localhost:8080/api/members -H "Authorization: Bearer $TOKEN"
```

Los endpoints `GET /api/members/{id}`, `PUT /api/members/{id}` y `DELETE /api/members/{id}` funcionan igual que los de libros.

### 5. Verificación de reglas y middlewares

* **Denegación sin token (`401 Unauthorized`):**

```bash
curl -i http://localhost:8080/api/books
```

* **Cabeceras CORS:**

```bash
curl -i -H "Origin: http://ejemplo.com" http://localhost:8080/health
```

* **Rastrear logs por solicitud:**

```bash
docker-compose logs gateway
```

Busca el identificador de rastreo `rid=<X-Request-ID>` en la salida.

> **Atención:** el límite predeterminado es de **60 peticiones por minuto por IP** (variable `RATE_LIMIT`). Al superarlo, la API devuelve `429 Too Many Requests`.

---

## Alternativa para Windows (PowerShell)

Los comandos anteriores usan sintaxis de bash (`\`, `$TOKEN`, comillas simples). En PowerShell usa estos equivalentes:

```powershell
# Estado del servicio
curl.exe http://localhost:8080/health

# Login y token
$r = Invoke-RestMethod -Method Post -Uri http://localhost:8080/auth/login -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
$h = @{ Authorization = "Bearer $($r.access_token)" }

# Crear un libro
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/books -Headers $h -ContentType "application/json; charset=utf-8" -Body '{"title":"Cien años de soledad","author":"Gabriel García Márquez","isbn":"9780307474728","year":1967,"copies_available":3}'

# Listar libros
Invoke-RestMethod -Uri http://localhost:8080/api/books -Headers $h

# Eliminar el libro 1
Invoke-RestMethod -Method Delete -Uri http://localhost:8080/api/books/1 -Headers $h
```

### Con Postman

1. Crea una petición `POST http://localhost:8080/auth/login` con *Body → raw → JSON*:
   `{"username":"admin","password":"admin123"}`.
2. Copia el `access_token` de la respuesta.
3. En las demás peticiones, abre *Authorization → Bearer Token* y pega el token.
4. Las rutas son las de la tabla de referencia de la siguiente sección.

---

## Referencia de la API

| Verbo | Ruta (Gateway) | Propósito |
| --- | --- | --- |
| `POST` | `/auth/login` | Emite el token JWT |
| `GET` | `/health` | Diagnóstico de disponibilidad del Gateway |
| `GET` / `POST` | `/api/books` | Consulta o registro de libros |
| `GET` / `PUT` / `DELETE` | `/api/books/{id}` | Operaciones sobre un libro |
| `GET` / `POST` | `/api/members` | Consulta o alta de socios |
| `GET` / `PUT` / `DELETE` | `/api/members/{id}` | Operaciones sobre un socio |

Las rutas `/api/*` requieren la cabecera `Authorization: Bearer <token>`. El Gateway quita el prefijo `/api` antes de reenviar la petición al microservicio.

### Códigos de estado esperados

* `200`: operación correcta.
* `201`: creado exitosamente.
* `204`: eliminado, sin contenido de retorno.
* `401`: token ausente, vencido o no válido (o credenciales incorrectas en el login).
* `404`: recurso no encontrado.
* `409`: dato duplicado (ISBN o correo ya existentes).
* `422`: datos de entrada inválidos.
* `429`: cuota de peticiones superada.
* `502`: fallo en la comunicación con el microservicio interno.

---

## Ejecución local sin Docker (opcional)

Este modo necesita un **PostgreSQL propio** escuchando en `localhost:5432` con la base `biblioteca` y el usuario `biblioteca` (en Docker Compose la base de datos no publica puertos).

1. Entra a la carpeta del servicio de libros y crea un entorno virtual:

```bash
cd books-service
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
```

2. Instala dependencias y levanta el servidor:

```bash
pip install -r requirements.txt
DATABASE_URL=postgresql+psycopg2://biblioteca:biblioteca123@localhost:5432/biblioteca uvicorn app.main:app --reload
```

En PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg2://biblioteca:biblioteca123@localhost:5432/biblioteca"
uvicorn app.main:app --reload
```

3. La documentación Swagger del microservicio queda en `http://localhost:8000/docs` (solo en este modo local).

---

## Estrategia de ramas (Git Flow)

```bash
# Inicio del proyecto
git init -b main
git add README.md .gitignore .env.example
git commit -m "chore: estructura inicial y README"
git checkout -b develop

# Microservicio
git checkout -b feature/books-service develop
git add books-service
git commit -m "feat: microservicio de libros y socios con CRUD"
git checkout develop
git merge --no-ff feature/books-service

# Gateway
git checkout -b feature/api-gateway develop
git add gateway
git commit -m "feat: gateway con CORS, logging, rate limit y JWT"
git checkout develop
git merge --no-ff feature/api-gateway

# Docker Compose
git checkout -b feature/docker-compose develop
git add docker-compose.yml
git commit -m "feat: orquestación con Docker Compose y healthchecks"
git checkout develop
git merge --no-ff feature/docker-compose

# Documentación
git checkout -b feature/documentacion develop
git add docs
git commit -m "docs: diagramas C4 e informe técnico"
git checkout develop
git merge --no-ff feature/documentacion

# Release y etiqueta de versión
git checkout -b release/1.0.0 develop
git checkout main
git merge --no-ff release/1.0.0
git tag v1.0.0
git checkout develop
git merge --no-ff release/1.0.0
```

Convención de mensajes de commit: `feat:`, `fix:`, `docs:`, `chore:`.
