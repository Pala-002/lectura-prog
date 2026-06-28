"""
Servicios para el sistema SIET
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import User, Role
from app.schemas.schemas import (
    UserCreate,
    UserUpdate,
    Token,
    REDTICScoreCreate,
    StroopResultCreate,
    NBackResultCreate,
    DigitSpanResultCreate,
    TrailMakingResultCreate,
    CRTResultCreate,
    ReportCreate
)
from app.repositories import (
    user_repository,
    role_repository,
    consent_repository,
    session_repository,
    redtic_score_repository,
    stroop_repository,
    nback_repository,
    digitspan_repository,
    trailmaking_repository,
    crt_repository,
    report_repository,
    learning_log_repository,
    behavior_log_repository
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import (
    UserNotFoundException,
    InvalidCredentialsException,
    ConsentNotGivenException
)
from app.core.config import settings


# ==================== USER SERVICE ====================

class UserService:
    """Servicio para gestión de usuarios"""
    
    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """
        Crea un nuevo usuario.
        
        Args:
            db: Sesión de base de datos
            user_in: Datos del usuario a crear
            
        Returns:
            Usuario creado
        """
        # Verificar que el rol existe
        role = role_repository.get(db, user_in.role_id)
        if not role:
            raise UserNotFoundException()
        
        # Verificar que el username no exista
        existing_user = user_repository.get_by_username(db, user_in.username)
        if existing_user:
            raise ValueError("El nombre de usuario ya está en uso")
        
        # Verificar que el email no exista
        existing_email = user_repository.get_by_email(db, user_in.email)
        if existing_email:
            raise ValueError("El email ya está registrado")
        
        # Crear usuario
        user_data = {
            "username": user_in.username,
            "email": user_in.email,
            "full_name": user_in.full_name,
            "password_hash": get_password_hash(user_in.password),
            "role_id": user_in.role_id,
            "is_active": True
        }
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def authenticate_user(
        self,
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Autentica un usuario.
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Usuario autenticado o None
        """
        user = user_repository.get_by_username(db, username)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def login(self, db: Session, username: str, password: str) -> Token:
        """
        Realiza login y retorna token.
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Token de acceso
        """
        user = self.authenticate_user(db, username, password)
        if not user:
            raise InvalidCredentialsException()
        
        access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    
    def get_user(self, db: Session, user_id: int) -> User:
        """
        Obtiene un usuario por ID.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Usuario
        """
        user = user_repository.get(db, user_id)
        if not user:
            raise UserNotFoundException(user_id=user_id)
        return user
    
    def update_user(
        self,
        db: Session,
        user_id: int,
        user_in: UserUpdate
    ) -> User:
        """
        Actualiza un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            user_in: Datos actualizados
            
        Returns:
            Usuario actualizado
        """
        user = self.get_user(db, user_id)
        
        update_data = user_in.dict(exclude_unset=True)
        
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    def get_users_by_role(self, db: Session, role_name: str) -> List[User]:
        """
        Obtiene usuarios por rol.
        
        Args:
            db: Sesión de base de datos
            role_name: Nombre del rol
            
        Returns:
            Lista de usuarios
        """
        role = role_repository.get_by_name(db, role_name)
        if not role:
            return []
        
        return user_repository.get_users_by_role(db, role.id)


# ==================== CONSENT SERVICE ====================

class ConsentService:
    """Servicio para gestión de consentimiento"""
    
    def give_consent(
        self,
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Registra consentimiento informado.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            ip_address: Dirección IP
            user_agent: User agent del navegador
            
        Returns:
            True si se registró correctamente
        """
        from app.models.models import Consent
        
        existing = consent_repository.get_by_user(db, user_id)
        if existing:
            return existing.accepted
        
        consent = Consent(
            user_id=user_id,
            accepted=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(consent)
        db.commit()
        
        return True
    
    def has_consent(self, db: Session, user_id: int) -> bool:
        """
        Verifica si un usuario ha dado consentimiento.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            True si ha dado consentimiento
        """
        return consent_repository.has_accepted(db, user_id)
    
    def require_consent(self, db: Session, user_id: int) -> None:
        """
        Requiere consentimiento para continuar.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Raises:
            ConsentNotGivenException: Si no ha dado consentimiento
        """
        if not self.has_consent(db, user_id):
            raise ConsentNotGivenException()


# ==================== SESSION SERVICE ====================

class SessionService:
    """Servicio para gestión de sesiones"""
    
    def start_session(self, db: Session, user_id: int) -> Any:
        """
        Inicia una nueva sesión.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Sesión creada
        """
        return session_repository.create_session(db, user_id)
    
    def end_session(self, db: Session, session_id: int) -> Any:
        """
        Finaliza una sesión.
        
        Args:
            db: Sesión de base de datos
            session_id: ID de la sesión
            
        Returns:
            Sesión finalizada
        """
        return session_repository.end_session(db, session_id)
    
    def get_active_session(self, db: Session, user_id: int) -> Optional[Any]:
        """
        Obtiene la sesión activa del usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Sesión activa o None
        """
        return session_repository.get_active_session(db, user_id)


user_service = UserService()
consent_service = ConsentService()
session_service = SessionService()
