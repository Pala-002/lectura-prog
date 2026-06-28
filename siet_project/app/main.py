"""
Aplicación principal FastAPI para SIET
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import Base, engine
from app.api.v1.api import api_router


# Crear tablas de base de datos al iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestor de ciclo de vida de la aplicación"""
    # Startup: crear tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear roles por defecto si no existen
    from sqlalchemy.orm import Session
    from app.models.models import Role
    
    with Session(engine) as session:
        roles = ["admin", "researcher", "student"]
        for role_name in roles:
            existing = session.query(Role).filter(Role.name == role_name).first()
            if not existing:
                role = Role(
                    name=role_name,
                    description=f"Rol {role_name} del sistema SIET"
                )
                session.add(role)
        session.commit()
    
    yield
    
    # Shutdown (limpieza si es necesaria)
    pass


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema Inteligente de Evaluación de Tecnoestrés",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir router de API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root(request: Request):
    """Página de inicio"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
