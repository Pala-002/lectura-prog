"""
Repositorios para el sistema SIET
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import (
    Role,
    User,
    Consent,
    Session as SessionModel,
    REDTICAnswer,
    REDTICScore,
    StroopResult,
    NBackResult,
    DigitSpanResult,
    TrailMakingResult,
    CRTResult,
    LearningLog,
    BehaviorLog,
    Report
)
from app.repositories.base import BaseRepository


# ==================== ROLE REPOSITORY ====================

class RoleRepository(BaseRepository[Role]):
    """Repositorio para roles"""
    
    def __init__(self):
        super().__init__(Role)
    
    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        """Obtiene un rol por nombre"""
        return db.query(Role).filter(Role.name == name).first()


role_repository = RoleRepository()


# ==================== USER REPOSITORY ====================

class UserRepository(BaseRepository[User]):
    """Repositorio para usuarios"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Obtiene un usuario por nombre de usuario"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtiene un usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_users_by_role(self, db: Session, role_id: int) -> List[User]:
        """Obtiene usuarios por rol"""
        return db.query(User).filter(User.role_id == role_id).all()
    
    def get_active_users(self, db: Session) -> List[User]:
        """Obtiene usuarios activos"""
        return db.query(User).filter(User.is_active == True).all()


user_repository = UserRepository()


# ==================== CONSENT REPOSITORY ====================

class ConsentRepository(BaseRepository[Consent]):
    """Repositorio para consentimiento informado"""
    
    def __init__(self):
        super().__init__(Consent)
    
    def get_by_user(self, db: Session, user_id: int) -> Optional[Consent]:
        """Obtiene consentimiento por usuario"""
        return db.query(Consent).filter(Consent.user_id == user_id).first()
    
    def has_accepted(self, db: Session, user_id: int) -> bool:
        """Verifica si un usuario ha aceptado el consentimiento"""
        consent = self.get_by_user(db, user_id)
        return consent is not None and consent.accepted


consent_repository = ConsentRepository()


# ==================== SESSION REPOSITORY ====================

class SessionRepository(BaseRepository[SessionModel]):
    """Repositorio para sesiones"""
    
    def __init__(self):
        super().__init__(SessionModel)
    
    def get_by_user(self, db: Session, user_id: int) -> List[SessionModel]:
        """Obtiene sesiones por usuario"""
        return db.query(SessionModel).filter(
            SessionModel.user_id == user_id
        ).order_by(SessionModel.created_at.desc()).all()
    
    def get_active_session(self, db: Session, user_id: int) -> Optional[SessionModel]:
        """Obtiene sesión activa del usuario"""
        return db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.status == "active"
        ).first()
    
    def create_session(self, db: Session, user_id: int) -> SessionModel:
        """Crea una nueva sesión"""
        session = SessionModel(user_id=user_id, status="active")
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def end_session(self, db: Session, session_id: int) -> Optional[SessionModel]:
        """Finaliza una sesión"""
        session = self.get(db, session_id)
        if session:
            session.status = "completed"
            session.end_time = datetime.utcnow()
            if session.start_time:
                duration = session.end_time - session.start_time
                session.total_duration = int(duration.total_seconds())
            db.commit()
            db.refresh(session)
        return session


session_repository = SessionRepository()


# ==================== REDTIC REPOSITORIES ====================

class REDTICAnswerRepository(BaseRepository[REDTICAnswer]):
    """Repositorio para respuestas RED-TIC"""
    
    def __init__(self):
        super().__init__(REDTICAnswer)
    
    def get_by_user(self, db: Session, user_id: int) -> List[REDTICAnswer]:
        """Obtiene respuestas por usuario"""
        return db.query(REDTICAnswer).filter(
            REDTICAnswer.user_id == user_id
        ).all()
    
    def get_by_session(self, db: Session, session_id: int) -> List[REDTICAnswer]:
        """Obtiene respuestas por sesión"""
        return db.query(REDTICAnswer).filter(
            REDTICAnswer.session_id == session_id
        ).all()


redtic_answer_repository = REDTICAnswerRepository()


class REDTICScoreRepository(BaseRepository[REDTICScore]):
    """Repositorio para puntajes RED-TIC"""
    
    def __init__(self):
        super().__init__(REDTICScore)
    
    def get_by_user(self, db: Session, user_id: int) -> List[REDTICScore]:
        """Obtiene puntajes por usuario"""
        return db.query(REDTICScore).filter(
            REDTICScore.user_id == user_id
        ).order_by(REDTICScore.created_at.desc()).all()
    
    def get_latest(self, db: Session, user_id: int) -> Optional[REDTICScore]:
        """Obtiene el puntaje más reciente"""
        return db.query(REDTICScore).filter(
            REDTICScore.user_id == user_id
        ).order_by(REDTICScore.created_at.desc()).first()


redtic_score_repository = REDTICScoreRepository()


# ==================== COGNITIVE TEST REPOSITORIES ====================

class StroopResultRepository(BaseRepository[StroopResult]):
    """Repositorio para resultados Stroop"""
    
    def __init__(self):
        super().__init__(StroopResult)
    
    def get_by_user(self, db: Session, user_id: int) -> List[StroopResult]:
        """Obtiene resultados por usuario"""
        return db.query(StroopResult).filter(
            StroopResult.user_id == user_id
        ).order_by(StroopResult.created_at.desc()).all()


stroop_repository = StroopResultRepository()


class NBackResultRepository(BaseRepository[NBackResult]):
    """Repositorio para resultados N-Back"""
    
    def __init__(self):
        super().__init__(NBackResult)
    
    def get_by_user(self, db: Session, user_id: int) -> List[NBackResult]:
        """Obtiene resultados por usuario"""
        return db.query(NBackResult).filter(
            NBackResult.user_id == user_id
        ).order_by(NBackResult.created_at.desc()).all()


nback_repository = NBackResultRepository()


class DigitSpanResultRepository(BaseRepository[DigitSpanResult]):
    """Repositorio para resultados Digit Span"""
    
    def __init__(self):
        super().__init__(DigitSpanResult)
    
    def get_by_user(self, db: Session, user_id: int) -> List[DigitSpanResult]:
        """Obtiene resultados por usuario"""
        return db.query(DigitSpanResult).filter(
            DigitSpanResult.user_id == user_id
        ).order_by(DigitSpanResult.created_at.desc()).all()


digitspan_repository = DigitSpanResultRepository()


class TrailMakingResultRepository(BaseRepository[TrailMakingResult]):
    """Repositorio para resultados Trail Making"""
    
    def __init__(self):
        super().__init__(TrailMakingResult)
    
    def get_by_user(self, db: Session, user_id: int) -> List[TrailMakingResult]:
        """Obtiene resultados por usuario"""
        return db.query(TrailMakingResult).filter(
            TrailMakingResult.user_id == user_id
        ).order_by(TrailMakingResult.created_at.desc()).all()


trailmaking_repository = TrailMakingResultRepository()


class CRTResultRepository(BaseRepository[CRTResult]):
    """Repositorio para resultados CRT"""
    
    def __init__(self):
        super().__init__(CRTResult)
    
    def get_by_user(self, db: Session, user_id: int) -> List[CRTResult]:
        """Obtiene resultados por usuario"""
        return db.query(CRTResult).filter(
            CRTResult.user_id == user_id
        ).order_by(CRTResult.created_at.desc()).all()


crt_repository = CRTResultRepository()


# ==================== ANALYTICS REPOSITORIES ====================

class LearningLogRepository(BaseRepository[LearningLog]):
    """Repositorio para logs de learning analytics"""
    
    def __init__(self):
        super().__init__(LearningLog)
    
    def get_by_user(self, db: Session, user_id: int) -> List[LearningLog]:
        """Obtiene logs por usuario"""
        return db.query(LearningLog).filter(
            LearningLog.user_id == user_id
        ).order_by(LearningLog.created_at.desc()).all()
    
    def get_by_session(self, db: Session, session_id: int) -> List[LearningLog]:
        """Obtiene logs por sesión"""
        return db.query(LearningLog).filter(
            LearningLog.session_id == session_id
        ).all()


learning_log_repository = LearningLogRepository()


class BehaviorLogRepository(BaseRepository[BehaviorLog]):
    """Repositorio para logs de behavioral analytics"""
    
    def __init__(self):
        super().__init__(BehaviorLog)
    
    def get_by_user(self, db: Session, user_id: int) -> List[BehaviorLog]:
        """Obtiene logs por usuario"""
        return db.query(BehaviorLog).filter(
            BehaviorLog.user_id == user_id
        ).order_by(BehaviorLog.created_at.desc()).all()
    
    def get_by_session(self, db: Session, session_id: int) -> List[BehaviorLog]:
        """Obtiene logs por sesión"""
        return db.query(BehaviorLog).filter(
            BehaviorLog.session_id == session_id
        ).all()


behavior_log_repository = BehaviorLogRepository()


# ==================== REPORT REPOSITORY ====================

class ReportRepository(BaseRepository[Report]):
    """Repositorio para reportes"""
    
    def __init__(self):
        super().__init__(Report)
    
    def get_by_user(self, db: Session, user_id: int) -> List[Report]:
        """Obtiene reportes por usuario"""
        return db.query(Report).filter(
            Report.user_id == user_id
        ).order_by(Report.created_at.desc()).all()
    
    def get_latest(self, db: Session, user_id: int) -> Optional[Report]:
        """Obtiene el reporte más reciente"""
        return db.query(Report).filter(
            Report.user_id == user_id
        ).order_by(Report.created_at.desc()).first()


report_repository = ReportRepository()
