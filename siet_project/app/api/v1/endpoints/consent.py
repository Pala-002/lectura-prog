"""
Endpoints de consentimiento informado
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.schemas import ConsentCreate, ConsentResponse
from app.services.user_services import consent_service
from app.models.models import Consent


router = APIRouter()


@router.post("/", response_model=ConsentResponse)
async def give_consent(
    consent_data: ConsentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Registrar consentimiento informado del usuario"""
    try:
        # Obtener IP y user agent del request si no se proporcionan
        ip_address = consent_data.ip_address or request.client.host
        user_agent = consent_data.user_agent or request.headers.get("user-agent")
        
        # Verificar si ya existe consentimiento
        existing = db.query(Consent).filter(Consent.user_id == consent_data.user_id).first()
        if existing:
            return existing
        
        # Crear nuevo consentimiento
        consent = Consent(
            user_id=consent_data.user_id,
            accepted=consent_data.accepted,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(consent)
        db.commit()
        db.refresh(consent)
        
        return consent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=Optional[ConsentResponse])
async def get_user_consent(user_id: int, db: Session = Depends(get_db)):
    """Obtener estado de consentimiento de un usuario"""
    consent = db.query(Consent).filter(Consent.user_id == user_id).first()
    return consent


@router.get("/check/{user_id}")
async def check_consent_status(user_id: int, db: Session = Depends(get_db)):
    """Verificar si un usuario ha dado consentimiento"""
    consent = db.query(Consent).filter(Consent.user_id == user_id).first()
    
    if not consent:
        return {"has_consent": False, "accepted": False}
    
    return {
        "has_consent": True,
        "accepted": consent.accepted,
        "accepted_at": consent.accepted_at.isoformat() if consent.accepted_at else None
    }
