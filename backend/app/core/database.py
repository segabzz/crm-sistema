from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# SQLite requiere check_same_thread=False para FastAPI multithreading
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import app.models  # noqa: F401 - Asegura que todos los modelos estén registrados en Base.metadata
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        for ddl in [
            "ALTER TABLE reviews ADD COLUMN estado_analisis VARCHAR(30) DEFAULT 'COMPLETADO'",
            "ALTER TABLE reviews ADD COLUMN pedido_id VARCHAR(36) REFERENCES orders(id) ON DELETE SET NULL",
        ]:
            try:
                conn.execute(text(ddl))
                conn.commit()
            except Exception:
                pass

def get_db():
    """Generador de dependencias de FastAPI para inyectar la sesión de DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
