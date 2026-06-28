"""
Endpoints de RED-TIC
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.schemas import (
    REDTICAnswerCreate,
    REDTICScoreResponse,
    REDTICAnswerResponse
)
from app.services.test_services import redtic_service
from app.models.models import REDTICAnswer, REDTICScore


router = APIRouter()


@router.post("/answers", response_model=REDTICScoreResponse)
async def submit_redtic_answers(
    answers: List[REDTICAnswerCreate],
    db: Session = Depends(get_db)
):
    """Enviar respuestas RED-TIC y obtener puntaje"""
    if not answers:
        raise HTTPException(status_code=400, detail="No se proporcionaron respuestas")
    
    try:
        # Obtener user_id y session_id de la primera respuesta
        user_id = answers[0].user_id
        session_id = answers[0].session_id
        
        # Guardar respuestas y calcular puntajes
        score = redtic_service.save_results(
            db=db,
            user_id=user_id,
            session_id=session_id,
            answers=answers
        )
        
        return score
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scores/user/{user_id}", response_model=List[REDTICScoreResponse])
async def get_user_scores(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los puntajes RED-TIC de un usuario"""
    scores = db.query(REDTICScore).filter(
        REDTICScore.user_id == user_id
    ).order_by(REDTICScore.created_at.desc()).all()
    
    return scores


@router.get("/answers/user/{user_id}", response_model=List[REDTICAnswerResponse])
async def get_user_answers(user_id: int, db: Session = Depends(get_db)):
    """Obtener todas las respuestas RED-TIC de un usuario"""
    answers = db.query(REDTICAnswer).filter(
        REDTICAnswer.user_id == user_id
    ).order_by(REDTICAnswer.created_at.desc()).all()
    
    return answers


@router.get("/latest/{user_id}", response_model=REDTICScoreResponse)
async def get_latest_score(user_id: int, db: Session = Depends(get_db)):
    """Obtener el último puntaje RED-TIC de un usuario"""
    score = db.query(REDTICScore).filter(
        REDTICScore.user_id == user_id
    ).order_by(REDTICScore.created_at.desc()).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="No se encontraron puntajes RED-TIC")
    
    return score
