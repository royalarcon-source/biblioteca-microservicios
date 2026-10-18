"""Genera los diagramas C4 (nivel 1 y 2) de la Biblioteca Digital.
Uso: python generar_c4.py  ->  c4-nivel1-contexto.png, c4-nivel2-contenedores.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Ellipse, Circle

PERSONA, SISTEMA, EXTERNO, CONTENEDOR = "#08427B", "#1168BD", "#7A7A7A", "#438DD5"
LINEA = "#333333"
plt.rcParams["font.family"] = "DejaVu Sans"


def caja(ax, cx, cy, w, h, color, nombre, tecnologia, lineas, persona=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0,rounding_size=0.15", fc=color, ec="none", zorder=2))
    if persona:
        ax.add_patch(Circle((cx, cy + h / 2 + 0.05), 0.32, fc=color, ec="white", lw=2, zorder=3))
    y = cy + h / 2 - 0.45
    ax.text(cx, y, nombre, ha="center", va="center", color="white", fontsize=13,
            fontweight="bold", zorder=4)
    ax.text(cx, y - 0.40, f"[{tecnologia}]", ha="center", va="center", color="#E8F0FA",
            fontsize=9.5, style="italic", zorder=4)
    ax.text(cx, y - 0.95 - 0.30 * (len(lineas) - 1) / 2, "\n".join(lineas), ha="center",
            va="center", color="white", fontsize=10, linespacing=1.35, zorder=4)


def base_datos(ax, cx, cy, w, h, color, nombre, tecnologia, lineas):
    e = 0.55
    x0, y0 = cx - w / 2, cy - h / 2
    ax.add_patch(Ellipse((cx, y0 + e / 2), w, e, fc=color, ec="none", zorder=2))
    ax.add_patch(Rectangle((x0, y0 + e / 2), w, h - e, fc=color, ec="none", zorder=2))
    ax.add_patch(Ellipse((cx, y0 + h - e / 2), w, e, fc="#6FA8DC", ec="white", lw=1, zorder=3))
    y = cy + 0.1
    ax.text(cx, y + 0.45, nombre, ha="center", va="center", color="white", fontsize=13,
            fontweight="bold", zorder=4)
    ax.text(cx, y + 0.05, f"[{tecnologia}]", ha="center", va="center", color="#E8F0FA",
            fontsize=9.5, style="italic", zorder=4)
    ax.text(cx, y - 0.50, "\n".join(lineas), ha="center", va="center", color="white",
            fontsize=10, linespacing=1.35, zorder=4)


def flecha(ax, p0, p1, etiqueta, off=(0, 0), ha="center"):
    ax.annotate("", xy=p1, xytext=p0, zorder=5,
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color=LINEA, shrinkA=0, shrinkB=0))
    mx, my = (p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1]
    ax.text(mx, my, etiqueta, ha=ha, va="center", fontsize=9.5, color=LINEA, zorder=6,
            linespacing=1.3, bbox=dict(fc="white", ec="none", pad=2))


def leyenda(ax, x, y, items):
    for i, (color, texto) in enumerate(items):
        xi = x + i * 3.3
        ax.add_patch(Rectangle((xi, y - 0.15), 0.3, 0.3, fc=color, ec="none"))
        ax.text(xi + 0.45, y, texto, va="center", fontsize=9.5, color=LINEA)


# ---------------- Nivel 1: Contexto ----------------
fig, ax = plt.subplots(figsize=(16, 6.2))
ax.set_xlim(0, 16); ax.set_ylim(0, 6.2); ax.axis("off")
ax.text(8, 5.8, "Diagrama C4 – Nivel 1: Contexto del sistema", ha="center", fontsize=15,
        fontweight="bold", color=LINEA)
ax.text(8, 5.4, "Sistema Biblioteca Digital", ha="center", fontsize=10.5, color="#666666")
cy, w, h = 2.9, 4.0, 2.7
caja(ax, 2.2, cy, w, h, PERSONA, "Bibliotecario", "Persona",
     ["Administra el catálogo de libros", "y el registro de socios"], persona=True)
caja(ax, 8.0, cy, w, h, EXTERNO, "Cliente HTTP", "Sistema externo",
     ["Postman, Swagger UI o cURL", "para consumir la API"])
caja(ax, 13.8, cy, w, h, SISTEMA, "Biblioteca Digital", "Sistema de software",
     ["API REST segura para gestionar", "libros y socios"])
flecha(ax, (4.2, cy), (6.0, cy), "Usa", off=(0, 0.3))
flecha(ax, (10.0, cy), (11.8, cy), "Consume la API\n[HTTP/JSON + JWT]", off=(0, 0.45))
leyenda(ax, 1.0, 0.5, [(PERSONA, "Persona"), (SISTEMA, "Sistema en alcance"),
                       (EXTERNO, "Sistema externo")])
fig.savefig("c4-nivel1-contexto.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------- Nivel 2: Contenedores ----------------
fig, ax = plt.subplots(figsize=(14, 13.8))
ax.set_xlim(0, 14); ax.set_ylim(0, 13.8); ax.axis("off")
ax.text(7, 13.45, "Diagrama C4 – Nivel 2: Contenedores", ha="center", fontsize=15,
        fontweight="bold", color=LINEA)
ax.text(7, 13.05, "Sistema Biblioteca Digital", ha="center", fontsize=10.5, color="#666666")
L, R, w, h = 3.6, 10.4, 5.2, 2.5

caja(ax, L, 11.0, w, h, PERSONA, "Bibliotecario", "Persona",
     ["Administra libros y socios"], persona=True)
caja(ax, R, 11.0, w, h, EXTERNO, "Cliente HTTP", "Sistema externo",
     ["Postman, Swagger UI o cURL"])

# Frontera del sistema (Docker Compose)
ax.add_patch(Rectangle((0.5, 1.0), 13.0, 7.7, fc="none", ec="#555555", lw=1.6,
                       ls=(0, (6, 4)), zorder=1))
ax.text(0.75, 8.4, "Biblioteca Digital  ·  Docker Compose, red bridge «biblioteca-net»",
        fontsize=10.5, fontweight="bold", color="#555555", va="center")

caja(ax, R, 6.2, w, h, CONTENEDOR, "API Gateway", "Contenedor: Python, FastAPI, httpx",
     ["Único punto de entrada (puerto 8080).", "CORS, logging, rate limit, JWT"])
caja(ax, L, 6.2, w, h, CONTENEDOR, "Microservicio de Biblioteca",
     "Contenedor: Python, FastAPI, SQLAlchemy",
     ["CRUD de libros y socios", "(Repository, DTO, DI)"])
base_datos(ax, L, 2.8, w, 2.5, CONTENEDOR, "Base de datos", "Contenedor: PostgreSQL 16",
           ["Almacena libros y socios", "(volumen pgdata)"])

flecha(ax, (L + w / 2, 11.0), (R - w / 2, 11.0), "Usa", off=(0, 0.3))
flecha(ax, (R, 11.0 - h / 2), (R, 6.2 + h / 2), "Peticiones HTTP/JSON\n(puerto 8080)", off=(0.2, 0.9), ha="left")
flecha(ax, (R - w / 2, 6.2), (L + w / 2, 6.2), "Redirige /api/*\n[HTTP/JSON]", off=(0, 0.5))
flecha(ax, (L, 6.2 - h / 2), (L, 2.8 + 1.25), "Lee y escribe\n[SQL, TCP 5432]", off=(0, 0))

leyenda(ax, 0.8, 0.45, [(PERSONA, "Persona"), (EXTERNO, "Sistema externo"),
                        (CONTENEDOR, "Contenedor"), ("#6FA8DC", "Base de datos")])
fig.savefig("c4-nivel2-contenedores.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("ok")
