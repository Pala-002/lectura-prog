"""
Endpoints de Analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.db.database import get_db
from app.schemas.schemas import (
    LearningLogCreate,
    LearningLogResponse,
    BehaviorLogCreate,
    BehaviorLogResponse
)
from app.services.analytics_services import analytics_engine
from app.models.models import LearningLog, BehaviorLog


router = APIRouter()


# ==================== LEARNING ANALYTICS ====================

@router.post("/learning/log", response_model=LearningLogResponse)
async def log_learning_event(
    log_data: LearningLogCreate,
    db: Session = Depends(get_db)
):
    """Registrar evento de learning analytics"""
    log = LearningLog(**log_data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/learning/user/{user_id}", response_model=list[LearningLogResponse])
async def get_user_learning_logs(
    user_id: int,
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtener logs de learning analytics de un usuario"""
    query = db.query(LearningLog).filter(LearningLog.user_id == user_id)
    
    if session_id:
        query = query.filter(LearningLog.session_id == session_id)
    
    logs = query.order_by(LearningLog.created_at.desc()).all()
    return logs


# ==================== BEHAVIORAL ANALYTICS ====================

@router.post("/behavior/log", response_model=BehaviorLogResponse)
async def log_behavior_event(
    log_data: BehaviorLogCreate,
    db: Session = Depends(get_db)
):
    """Registrar evento de behavioral analytics"""
    log = BehaviorLog(**log_data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/behavior/user/{user_id}", response_model=list[BehaviorLogResponse])
async def get_user_behavior_logs(
    user_id: int,
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtener logs de behavioral analytics de un usuario"""
    query = db.query(BehaviorLog).filter(BehaviorLog.user_id == user_id)
    
    if session_id:
        query = query.filter(BehaviorLog.session_id == session_id)
    
    logs = query.order_by(BehaviorLog.created_at.desc()).all()
    return logs


# ==================== ANALYTICS ENGINE ====================

@router.get("/technostress/{user_id}")
async def get_technostress_analysis(user_id: int, db: Session = Depends(get_db)):
    """Obtener análisis de tecnoestrés"""
    result = analytics_engine.calculate_technostress_score(db, user_id)
    return result


@router.get("/cognitive/{user_id}")
async def get_cognitive_analysis(user_id: int, db: Session = Depends(get_db)):
    """Obtener análisis cognitivo"""
    result = analytics_engine.calculate_cognitive_score(db, user_id)
    return result


@router.get("/behavior/{user_id}")
async def get_behavior_analysis(
    user_id: int,
    session_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtener análisis de comportamiento"""
    result = analytics_engine.calculate_behavior_score(db, user_id, session_id)
    return result


@router.get("/overall/{user_id}")
async def get_overall_analysis(user_id: int, db: Session = Depends(get_db)):
    """Obtener análisis overall combinado"""
    technostress_data = analytics_engine.calculate_technostress_score(db, user_id)
    cognitive_data = analytics_engine.calculate_cognitive_score(db, user_id)
    behavior_data = analytics_engine.calculate_behavior_score(db, user_id)
    
    overall = analytics_engine.calculate_overall_score(
        technostress_data["global_score"],
        cognitive_data["global_score"],
        behavior_data["global_score"]
    )
    
    return overall
