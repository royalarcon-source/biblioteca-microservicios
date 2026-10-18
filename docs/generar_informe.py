# -*- coding: utf-8 -*-
"""Genera el informe técnico en PDF.

Antes de ejecutarlo:
  1. Completa las variables de la portada (MATERIA, DOCENTE, REPO_URL).
  2. Guarda tus capturas en docs/capturas/ con los nombres de la lista CAPTURAS.
  3. python generar_informe.py
Las capturas que no existan aparecen como recuadros vacíos.
"""
import os
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (Flowable, HRFlowable, Image, KeepTogether, PageBreak,
                                Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
                                XPreformatted)

# ------------------ Datos de la portada ------------------
NOMBRE = "Brayan Chambi"
MATERIA = ""      # ej. "Arquitectura de Software"
DOCENTE = ""      # ej. "Ing. ..."
REPO_URL = ""     # ej. "https://github.com/usuario/biblioteca-microservicios"
FECHA = "18 de octubre de 2026"

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "Informe_Tecnico_Biblioteca_Digital.pdf")
AZUL = colors.HexColor("#1F3A5F")
GRIS = colors.HexColor("#F3F4F6")

# archivo en docs/capturas  ->  pie de figura
CAPTURAS = [
    ("01_compose_ps.png", "Los tres contenedores en ejecución y en estado healthy (docker-compose ps)."),
    ("02_login.png", "POST /auth/login: respuesta 200 con el token JWT."),
    ("03_sin_token.png", "GET /api/books sin token: el gateway responde 401."),
    ("04_crear_libro.png", "POST /api/books: libro creado, respuesta 201."),
    ("05_listar_obtener.png", "GET /api/books y GET /api/books/{id}: respuestas 200."),
    ("06_actualizar_eliminar.png", "PUT /api/books/{id} (200) y DELETE /api/books/{id} (204)."),
    ("07_duplicado_409.png", "Intento de registrar un ISBN repetido: respuesta 409."),
    ("08_logs_gateway.png", "Logs del gateway (docker-compose logs gateway) con el rid de cada petición."),
]

# ------------------ Estilos ------------------
base = dict(fontName="Helvetica", fontSize=10.5, leading=14.8, alignment=TA_LEFT, textColor=colors.HexColor("#222222"))
P = ParagraphStyle("p", spaceAfter=7, **base)
PK = ParagraphStyle("pk", parent=P, keepWithNext=1)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=AZUL, spaceBefore=6, spaceAfter=8, keepWithNext=1)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=AZUL, spaceBefore=6, spaceAfter=4, keepWithNext=1)
CAP = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=colors.HexColor("#555555"), spaceAfter=10, alignment=1)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=11.5)
CELLB = ParagraphStyle("cellb", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
CODE = ParagraphStyle("code", fontName="Courier", fontSize=8.3, leading=10.4)


def codigo(texto):
    t = Table([[XPreformatted(texto, CODE)]], colWidths=[16.2 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GRIS),
                           ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D4DA")),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def tabla(filas, anchos, cabecera=True):
    data = [[Paragraph(c, CELLB if (cabecera and i == 0) else CELL) for c in fila] for i, fila in enumerate(filas)]
    t = Table(data, colWidths=anchos, repeatRows=1 if cabecera else 0)
    est = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9CED6")),
           ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if cabecera:
        est.append(("BACKGROUND", (0, 0), (-1, 0), AZUL))
    t.setStyle(TableStyle(est))
    return t


def figura(ruta, ancho_cm, alto_max_cm, pie):
    w, h = PILImage.open(ruta).size
    ancho = ancho_cm * cm
    alto = ancho * h / w
    if alto > alto_max_cm * cm:
        alto = alto_max_cm * cm
        ancho = alto * w / h
    return KeepTogether([Image(ruta, width=ancho, height=alto), Spacer(1, 3), Paragraph(pie, CAP)])


class Recuadro(Flowable):
    def __init__(self, texto, ancho=15 * cm, alto=3.4 * cm):
        super().__init__()
        self.texto, self.width, self.height = texto, ancho, alto

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.HexColor("#9AA3AF")); c.setDash(4, 3); c.setFillColor(colors.HexColor("#FAFAFA"))
        c.rect(0, 0, self.width, self.height, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#6B7280")); c.setFont("Helvetica", 9)
        c.drawCentredString(self.width / 2, self.height / 2 - 3, self.texto)


def pie_pagina(c, doc):
    if doc.page == 1:
        return
    c.saveState()
    c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#777777"))
    c.drawString(2.2 * cm, 1.3 * cm, f"{NOMBRE} · Biblioteca Digital: API Gateway y microservicio")
    c.drawRightString(letter[0] - 2.2 * cm, 1.3 * cm, f"Página {doc.page}")
    c.setStrokeColor(colors.HexColor("#DDDDDD")); c.line(2.2 * cm, 1.7 * cm, letter[0] - 2.2 * cm, 1.7 * cm)
    c.restoreState()


s = []

# ------------------ Portada ------------------
s += [Spacer(1, 5.5 * cm),
      Paragraph("Informe técnico", ParagraphStyle("t0", fontName="Helvetica", fontSize=15, textColor=colors.HexColor("#666666"), spaceAfter=6)),
      Paragraph("Biblioteca Digital", ParagraphStyle("t1", fontName="Helvetica-Bold", fontSize=32, leading=38, textColor=AZUL)),
      Paragraph("API Gateway y microservicio con FastAPI, PostgreSQL y Docker",
                ParagraphStyle("t2", fontName="Helvetica", fontSize=14, leading=19, textColor=colors.HexColor("#444444"), spaceAfter=14)),
      HRFlowable(width="100%", thickness=2, color=AZUL, spaceAfter=18)]
datos = [("Estudiante", NOMBRE), ("Tecnología asignada", "FastAPI (Python)"), ("Materia", MATERIA),
         ("Docente", DOCENTE), ("Repositorio", REPO_URL), ("Fecha", FECHA)]
for k, v in datos:
    if v:
        s.append(Paragraph(f"<b>{k}:</b> {v}", ParagraphStyle("d", parent=P, fontSize=11.5, leading=17, spaceAfter=3)))
s.append(PageBreak())

# ------------------ 1. Dominio ------------------
s += [Paragraph("1. Descripción del dominio", H1),
      Paragraph("La biblioteca de un colegio o de un barrio suele llevar su catálogo en cuadernos o en una hoja de cálculo "
                "compartida. Con el tiempo pasa lo de siempre: el mismo libro queda registrado dos veces con datos distintos, "
                "nadie sabe con certeza cuántas copias hay disponibles y la lista de socios está en otro archivo, a veces en "
                "otra computadora.", P),
      Paragraph("Este proyecto propone un sistema pequeño, la <b>Biblioteca Digital</b>, que reúne esa información en un solo "
                "lugar y la ofrece mediante una API REST. El bibliotecario, o la aplicación que use, puede registrar, consultar, "
                "modificar y eliminar libros y socios sin tocar la base de datos directamente.", P),
      Paragraph("El alcance se limita a dos entidades. Un <b>libro</b> tiene título, autor, ISBN, año y número de copias "
                "disponibles; un <b>socio</b> tiene nombre completo y correo. El ISBN y el correo son únicos, así que el sistema "
                "rechaza los duplicados. El registro de préstamos no entra en esta entrega, pero la estructura permite añadirlo "
                "después como una entidad nueva sin modificar las existentes.", P),
      Paragraph("¿Por qué un gateway delante del servicio?", H2),
      Paragraph("Porque deja al microservicio fuera del alcance directo de los clientes. Toda petición pasa primero por un único "
                "punto donde se controla quién entra (JWT), cuántas veces puede hacerlo (rate limiting) y qué queda registrado en "
                "los logs. El servicio de libros se dedica solo a la lógica del negocio y a los datos.", P)]

# ------------------ 2. Arquitectura ------------------
s += [Paragraph("2. Arquitectura (modelo C4)", H1),
      Paragraph("El sistema se describe en dos niveles del modelo C4: el contexto, que lo muestra desde fuera, y los "
                "contenedores, que muestran lo que hay dentro.", P),
      Paragraph("2.1 Nivel 1: contexto", H2),
      Paragraph("Intervienen tres elementos: el bibliotecario, que administra el catálogo; un cliente HTTP (en las pruebas, "
                "Postman, Swagger o cURL, aunque podría ser una página web) y el sistema Biblioteca Digital. Quien usa el sistema "
                "nunca le habla directamente: lo hace a través de un cliente que envía peticiones HTTP con JSON y un token JWT.", P),
      figura(os.path.join(AQUI, "c4-nivel1-contexto.png"), 16.2, 8, "Figura 1. Diagrama C4, nivel 1 (contexto).")]
s += [PageBreak(),
      Paragraph("2.2 Nivel 2: contenedores", H2),
      Paragraph("Dentro del sistema hay tres contenedores Docker unidos por la red bridge <i>biblioteca-net</i>. El API Gateway es "
                "el único que publica un puerto hacia fuera (8080). Valida el token y reenvía lo que llega a <font name='Courier'>/api/*</font> "
                "al microservicio, que escucha en el puerto 8000 solo dentro de la red interna. El microservicio guarda los datos en "
                "PostgreSQL, que tampoco es accesible desde el equipo anfitrión.", P),
      figura(os.path.join(AQUI, "c4-nivel2-contenedores.png"), 12.2, 12.5, "Figura 2. Diagrama C4, nivel 2 (contenedores)."),
      Paragraph("2.3 Decisiones de diseño", H2),
      Paragraph("<b>Gateway en FastAPI.</b> Se pudo usar Nginx, pero validar JWT y escribir el rate limiting resulta más directo en "
                "Python, y los cuatro mecanismos quedan en un solo archivo (<font name='Courier'>gateway/app/main.py</font>).", P),
      Paragraph("<b>Microservicio por capas.</b> Los routers solo manejan HTTP; el acceso a datos está en un repositorio genérico "
                "(<font name='Courier'>repository.py</font>) y los esquemas de Pydantic hacen de DTO, de modo que los modelos de "
                "SQLAlchemy no se exponen. La sesión de base de datos y los repositorios se inyectan con <font name='Courier'>Depends</font>.", P),
      Paragraph("<b>Tablas al arrancar.</b> El servicio crea las tablas con SQLAlchemy al iniciar. Para un proyecto de este tamaño "
                "evita montar migraciones, aunque en producción convendría usar Alembic.", P)]

# ------------------ 3. Gateway ------------------
s += [Paragraph("3. API Gateway: funciones transversales", H1),
      Paragraph("El gateway implementa cuatro mecanismos, dos más de los que pedía la consigna:", PK),
      tabla([["Mecanismo", "Cómo funciona"],
             ["CORS", "<font name='Courier'>CORSMiddleware</font> permite cualquier origen, método y cabecera (útil en desarrollo; en "
                      "producción se limitaría a los dominios conocidos) y expone <font name='Courier'>X-Request-ID</font>."],
             ["Logging y trazabilidad", "Cada petición lleva un <font name='Courier'>X-Request-ID</font>: el que envía el cliente o un UUID "
                      "generado. Se registran método, ruta, código de respuesta y tiempo en milisegundos, y el mismo id se reenvía al microservicio."],
             ["Rate limiting", "Ventana deslizante en memoria por IP: 60 peticiones por minuto (variable <font name='Courier'>RATE_LIMIT</font>). "
                      "Al superarlo responde 429 con <font name='Courier'>Retry-After</font>. <font name='Courier'>/health</font> y las peticiones OPTIONS quedan exentas."],
             ["Validación JWT", "<font name='Courier'>/auth/login</font> emite un token HS256 con vigencia de 60 minutos. Todas las rutas "
                      "<font name='Courier'>/api/*</font> exigen <font name='Courier'>Authorization: Bearer</font>; si falta o es inválido, 401."]],
            [3.6 * cm, 12.6 * cm]),
      Spacer(1, 6)]

# ------------------ 4. Endpoints ------------------
s += [Paragraph("4. Documentación de endpoints", H1),
      Paragraph("Todo se consume a través del gateway, en <font name='Courier'>http://localhost:8080</font>. El gateway quita el prefijo "
                "<font name='Courier'>/api</font> antes de reenviar, así que <font name='Courier'>/api/books</font> llega al microservicio "
                "como <font name='Courier'>/books</font>.", PK),
      tabla([["Método", "URL", "Descripción", "Respuestas"],
             ["POST", "/auth/login", "Obtiene un token JWT", "200, 401"],
             ["GET", "/health", "Estado del gateway", "200"],
             ["GET", "/api/books", "Lista libros (parámetros skip y limit)", "200"],
             ["GET", "/api/books/{id}", "Obtiene un libro", "200, 404"],
             ["POST", "/api/books", "Crea un libro", "201, 409, 422"],
             ["PUT", "/api/books/{id}", "Reemplaza los datos de un libro", "200, 404, 409, 422"],
             ["DELETE", "/api/books/{id}", "Elimina un libro", "204, 404"],
             ["GET", "/api/members", "Lista socios", "200"],
             ["GET", "/api/members/{id}", "Obtiene un socio", "200, 404"],
             ["POST", "/api/members", "Crea un socio", "201, 409, 422"],
             ["PUT", "/api/members/{id}", "Reemplaza los datos de un socio", "200, 404, 409, 422"],
             ["DELETE", "/api/members/{id}", "Elimina un socio", "204, 404"]],
            [1.8 * cm, 4.1 * cm, 7.0 * cm, 3.3 * cm]),
      Spacer(1, 6),
      Paragraph("Validaciones: título y autor no pueden estar vacíos; el ISBN tiene entre 10 y 20 caracteres; el año va de 0 a 2100; "
                "las copias no pueden ser negativas y el correo debe tener formato válido. Si algo falla, el servicio responde 422.", P),
      Paragraph("Ejemplos de peticiones y respuestas", H2),
      Paragraph("<b>Login</b> (<font name='Courier'>POST /auth/login</font>)", PK),
      codigo('Petición:   {"username": "admin", "password": "admin123"}\n'
             'Respuesta:  {"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer"}'),
      Spacer(1, 6),
      Paragraph("<b>Crear libro</b> (<font name='Courier'>POST /api/books</font>, respuesta 201)", PK),
      codigo('Petición:\n'
             '{\n  "title": "Cien años de soledad",\n  "author": "Gabriel García Márquez",\n  "isbn": "9780307474728",\n'
             '  "year": 1967,\n  "copies_available": 3\n}\n\n'
             'Respuesta:\n'
             '{\n  "title": "Cien años de soledad",\n  "author": "Gabriel García Márquez",\n  "isbn": "9780307474728",\n'
             '  "year": 1967,\n  "copies_available": 3,\n  "id": 1,\n  "created_at": "2026-10-18T15:02:11.482913Z"\n}'),
      Spacer(1, 6),
      Paragraph("<b>Crear socio</b> (<font name='Courier'>POST /api/members</font>, respuesta 201)", PK),
      codigo('Petición:   {"full_name": "Brayan Chambi", "email": "brayan@example.com"}\n'
             'Respuesta:  {"full_name": "Brayan Chambi", "email": "brayan@example.com", "id": 1, "created_at": "..."}'),
      Spacer(1, 6),
      Paragraph("<b>Errores</b>", PK),
      codigo('401 (sin token):      {"detail": "Falta el token Bearer"}\n'
             '404 (no existe):      {"detail": "Libro no encontrado"}\n'
             '409 (ISBN repetido):  {"detail": "Ya existe un libro con ese ISBN"}\n'
             '429 (rate limit):     {"detail": "Demasiadas peticiones, intenta más tarde"}')]

# ------------------ 5. Docker ------------------
s += [Paragraph("5. Contenerización", H1),
      Paragraph("El gateway y el microservicio tienen su propio Dockerfile, basado en <font name='Courier'>python:3.12-slim</font>. "
                "Primero se copia <font name='Courier'>requirements.txt</font> y se instalan las dependencias, y recién después el código, "
                "para que Docker reutilice esa capa mientras solo cambie el código. El proceso corre con un usuario sin privilegios.", P),
      Paragraph("El archivo <font name='Courier'>docker-compose.yml</font> define tres servicios en la red bridge <i>biblioteca-net</i>. "
                "El arranque está encadenado con <font name='Courier'>depends_on</font> y <font name='Courier'>condition: service_healthy</font>: "
                "primero PostgreSQL (healthcheck con <font name='Courier'>pg_isready</font>), luego el microservicio y al final el gateway. "
                "Los dos servicios de Python comprueban su salud llamando a <font name='Courier'>/health</font> con <font name='Courier'>urllib</font>, "
                "porque la imagen slim no trae curl.", P),
      Paragraph("Los datos de PostgreSQL viven en el volumen <font name='Courier'>pgdata</font> y sobreviven a un <font name='Courier'>docker-compose down</font>. "
                "Las credenciales y el secreto JWT se leen de variables de entorno (archivo <font name='Courier'>.env</font>), con valores por defecto "
                "para desarrollo.", P)]

# ------------------ 6. Pruebas ------------------
s += [Paragraph("6. Evidencia de pruebas", H1),
      Paragraph("Las capturas se tomaron con el sistema levantado con <font name='Courier'>docker-compose up --build</font>.", PK)]
for i, (arch, pie) in enumerate(CAPTURAS, 1):
    ruta = os.path.join(AQUI, "capturas", arch)
    if os.path.exists(ruta):
        s.append(figura(ruta, 15.5, 5.6, f"Captura {i}. {pie}"))
    else:
        s.append(KeepTogether([Recuadro(f"Captura pendiente: docs/capturas/{arch}", ancho=15.5 * cm, alto=3.0 * cm),
                               Spacer(1, 3), Paragraph(f"Captura {i}. {pie}", CAP)]))

# ------------------ 7. Conclusiones ------------------
s += [Paragraph("7. Conclusiones y limitaciones", H1),
      Paragraph("La arquitectura cumple lo planteado: un único punto de entrada, un servicio con CRUD completo sobre dos entidades, "
                "persistencia en PostgreSQL y todo el conjunto levantándose con un solo comando.", P),
      Paragraph("Quedan algunos límites conocidos. El rate limiting guarda los contadores en memoria, así que no se compartiría entre varias "
                "réplicas del gateway (para eso haría falta algo como Redis). Hay un solo usuario administrador definido por variables de "
                "entorno, CORS está abierto a cualquier origen y todavía no existe el registro de préstamos. Son mejoras razonables para una "
                "siguiente versión.", P)]

doc = SimpleDocTemplate(SALIDA, pagesize=letter, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.0 * cm, bottomMargin=2.4 * cm,
                        title="Informe técnico: Biblioteca Digital", author=NOMBRE)
doc.build(s, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("PDF generado:", SALIDA)
