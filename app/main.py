# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Config centralizada (ya existente)
from app.core.config import settings

# Routers actuales
from app.api.routes.consultas_eventos import router as consultas_router

from app.api.routes.eventos import router as eventos_router

# Publica todas las rutas de "eventos" bajo el prefijo /api/v1
app.include_router(eventos_router, prefix="/api/v1")  # ← monta el router de eventos en la app

from app.api.routes.representante import router as representantes_router
app.include_router(representantes_router, prefix="/api/v1")  # monta subrutas /api/v1/eventos/{id_evento}/organizaciones




app = FastAPI(
    title=settings.APP_NAME,
    description="API para registro, evaluación y consultas analíticas de eventos académicos/lúdicos.",
    version=settings.APP_VERSION,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers /api/v1 ---
# Si en el futuro creas un agregador (api_router_v1), usa:
# app.include_router(api_router_v1, prefix="/api/v1")
# Por ahora montamos routers individuales:
app.include_router(consultas_router, prefix="/api/v1")
# app.include_router(eventos_router, prefix="/api/v1")
# app.include_router(usuarios_router, prefix="/api/v1")
# app.include_router(organizaciones_router, prefix="/api/v1")
# app.include_router(evaluaciones_router, prefix="/api/v1")
# app.include_router(notificaciones_router, prefix="/api/v1")

# --- Redirección raíz a /docs ---
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

