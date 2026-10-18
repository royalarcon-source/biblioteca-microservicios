"""API Gateway (proxy inverso) de la Biblioteca Digital.

Características transversales:
  1. CORS
  2. Logging / tracing centralizado (X-Request-ID)
  3. Rate limiting por IP
  4. Validación de tokens JWT
"""
import logging
import os
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

BACKEND_URL = os.getenv("BACKEND_URL", "http://books-service:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # peticiones por ventana
RATE_WINDOW = 60  # segundos

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("gateway")

app = FastAPI(title="API Gateway - Biblioteca Digital", version="1.0.0")

# ---------- Rate limiting (ventana deslizante en memoria) ----------
_hits: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path == "/health":
        return await call_next(request)
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    q = _hits[ip]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        return JSONResponse(
            {"detail": "Demasiadas peticiones, intenta más tarde"},
            status_code=429,
            headers={"Retry-After": str(RATE_WINDOW)},
        )
    q.append(now)
    return await call_next(request)


# ---------- Logging / tracing ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    logger.info(
        "rid=%s %s %s -> %s (%.1f ms)",
        request_id, request.method, request.url.path, response.status_code, ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response


# ---------- CORS (se agrega al final para que sea la capa más externa) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# ---------- Endpoints propios del gateway ----------
class LoginIn(BaseModel):
    username: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.post("/auth/login")
def login(data: LoginIn):
    if data.username != ADMIN_USER or data.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    payload = {
        "sub": data.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# ---------- Proxy inverso: /api/* -> microservicio ----------
_SKIP_HEADERS = {"host", "content-length", "connection"}


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(path: str, request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta el token Bearer")
    try:
        jwt.decode(auth[7:], JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    headers = {k: v for k, v in request.headers.items() if k.lower() not in _SKIP_HEADERS}
    headers["X-Request-ID"] = getattr(request.state, "request_id", str(uuid.uuid4()))
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.request(
                request.method,
                f"{BACKEND_URL}/{path}",
                params=request.query_params,
                content=body,
                headers=headers,
            )
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Microservicio no disponible")

    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type"),
    )
