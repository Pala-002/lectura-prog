"""
Endpoints de Pruebas Cognitivas
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.schemas import (
    StroopResultCreate,
    StroopResultResponse,
    NBackResultCreate,
    NBackResultResponse,
    DigitSpanResultCreate,
    DigitSpanResultResponse,
    TrailMakingResultCreate,
    TrailMakingResultResponse,
    CRTResultCreate,
    CRTResultResponse
)
from app.services.test_services import cognitive_tests_service
from app.models.models import (
    StroopResult,
    NBackResult,
    DigitSpanResult,
    TrailMakingResult,
    CRTResult
)


router = APIRouter()


# ==================== STROOP ====================

@router.post("/stroop", response_model=StroopResultResponse)
async def submit_stroop_result(
    result: StroopResultCreate,
    db: Session = Depends(get_db)
):
    """Enviar resultado de prueba Stroop"""
    saved_result = cognitive_tests_service.save_stroop_result(db, result)
    return saved_result


@router.get("/stroop/user/{user_id}", response_model=List[StroopResultResponse])
async def get_user_stroop_results(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los resultados Stroop de un usuario"""
    results = db.query(StroopResult).filter(
        StroopResult.user_id == user_id
    ).order_by(StroopResult.created_at.desc()).all()
    
    return results


# ==================== N-BACK ====================

@router.post("/nback", response_model=NBackResultResponse)
async def submit_nback_result(
    result: NBackResultCreate,
    db: Session = Depends(get_db)
):
    """Enviar resultado de prueba N-Back"""
    saved_result = cognitive_tests_service.save_nback_result(db, result)
    return saved_result


@router.get("/nback/user/{user_id}", response_model=List[NBackResultResponse])
async def get_user_nback_results(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los resultados N-Back de un usuario"""
    results = db.query(NBackResult).filter(
        NBackResult.user_id == user_id
    ).order_by(NBackResult.created_at.desc()).all()
    
    return results


# ==================== DIGIT SPAN ====================

@router.post("/digitspan", response_model=DigitSpanResultResponse)
async def submit_digitspan_result(
    result: DigitSpanResultCreate,
    db: Session = Depends(get_db)
):
    """Enviar resultado de prueba Digit Span"""
    saved_result = cognitive_tests_service.save_digitspan_result(db, result)
    return saved_result


@router.get("/digitspan/user/{user_id}", response_model=List[DigitSpanResultResponse])
async def get_user_digitspan_results(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los resultados Digit Span de un usuario"""
    results = db.query(DigitSpanResult).filter(
        DigitSpanResult.user_id == user_id
    ).order_by(DigitSpanResult.created_at.desc()).all()
    
    return results


# ==================== TRAIL MAKING ====================

@router.post("/trailmaking", response_model=TrailMakingResultResponse)
async def submit_trailmaking_result(
    result: TrailMakingResultCreate,
    db: Session = Depends(get_db)
):
    """Enviar resultado de prueba Trail Making"""
    saved_result = cognitive_tests_service.save_trailmaking_result(db, result)
    return saved_result


@router.get("/trailmaking/user/{user_id}", response_model=List[TrailMakingResultResponse])
async def get_user_trailmaking_results(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los resultados Trail Making de un usuario"""
    results = db.query(TrailMakingResult).filter(
        TrailMakingResult.user_id == user_id
    ).order_by(TrailMakingResult.created_at.desc()).all()
    
    return results


# ==================== CRT ====================

@router.post("/crt", response_model=CRTResultResponse)
async def submit_crt_result(
    result: CRTResultCreate,
    db: Session = Depends(get_db)
):
    """Enviar resultado de Cognitive Reflection Test"""
    saved_result = cognitive_tests_service.save_crt_result(db, result)
    return saved_result


@router.get("/crt/user/{user_id}", response_model=List[CRTResultResponse])
async def get_user_crt_results(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los resultados CRT de un usuario"""
    results = db.query(CRTResult).filter(
        CRTResult.user_id == user_id
    ).order_by(CRTResult.created_at.desc()).all()
    
    return results
