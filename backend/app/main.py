from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal, init_db
from app.db.seed import seed_dishes
from app.api.v1.api import api_router

# Garantizar esquema actualizado al importar la app (útil para TestClient sin lifespan)
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de tablas y seed automático en startup
    print("[Startup] Inicializando tablas SQLite...")
    init_db()
    
    db = SessionLocal()
    try:
        insertados = seed_dishes(db)
        if insertados:
            print(f"[Startup] Catálogo inicial sembrado con {len(insertados)} platillos.")
        else:
            print("[Startup] Catálogo de platillos ya cargado previamente.")
    finally:
        db.close()
        
    yield
    print("[Shutdown] Finalizando servicio backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS para comunicación fluida con el frontend React/Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Estado"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }
