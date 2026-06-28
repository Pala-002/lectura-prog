"""
Router principal de API v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    consent,
    redtic,
    cognitive_tests,
    analytics,
    dashboard
)


api_router = APIRouter()

# Autenticación
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])

# Usuarios
api_router.include_router(users.router, prefix="/users", tags=["Usuarios"])

# Consentimiento
api_router.include_router(consent.router, prefix="/consent", tags=["Consentimiento"])

# RED-TIC
api_router.include_router(redtic.router, prefix="/redtic", tags=["RED-TIC"])

# Pruebas Cognitivas
api_router.include_router(
    cognitive_tests.router,
    prefix="/cognitive-tests",
    tags=["Pruebas Cognitivas"]
)

# Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
