"""
Servicio de login para SIET
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.models.models import User, Session as SessionModel
from app.repositories import user_repository, session_repository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings


class LoginService:
    """Servicio para autenticación de usuarios"""
    
    def authenticate(
        self,
        db: Session,
        email: str,
        password: str
    ) -> Tuple[Optional[User], str]:
        """
        Autentica un usuario con email y contraseña.
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña
            
        Returns:
            Tuple (Usuario autenticado o None, mensaje de error)
        """
        # Buscar por email
        user = user_repository.get_by_email(db, email)
        
        if not user:
            return None, "Credenciales inválidas"
        
        if not user.is_active or user.status != "active":
            return None, "Usuario inactivo. Contacte al administrador"
        
        if not verify_password(password, user.password_hash):
            return None, "Credenciales inválidas"
        
        return user, ""
    
    def login(
        self,
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> dict:
        """
        Realiza login y retorna tokens de acceso.
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña
            ip_address: Dirección IP del cliente
            user_agent: User agent del navegador
            
        Returns:
            Diccionario con access_token, refresh_token y user info
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Autenticar usuario
        user, error_msg = self.authenticate(db, email, password)
        
        if not user:
            raise ValueError(error_msg)
        
        # Crear tokens
        access_token = create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "role": user.role.name if user.role else "unknown",
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        )
        
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Crear sesión
        new_session = session_repository.create_session(db, user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "uuid": user.uuid,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}",
                "career": user.career,
                "semester": user.semester,
                "role": user.role.name if user.role else None,
                "role_id": user.role_id
            },
            "session_id": new_session.id
        }
    
    def logout(
        self,
        db: Session,
        session_id: int,
        user_id: int
    ) -> bool:
        """
        Cierra la sesión del usuario.
        
        Args:
            db: Sesión de base de datos
            session_id: ID de la sesión a cerrar
            user_id: ID del usuario
            
        Returns:
            True si se cerró correctamente
        """
        session = session_repository.end_session(db, session_id)
        return session is not None
    
    def refresh_token(
        self,
        db: Session,
        refresh_token: str
    ) -> dict:
        """
        Renueva el token de acceso usando el refresh token.
        
        Args:
            db: Sesión de base de datos
            refresh_token: Refresh token válido
            
        Returns:
            Nuevo access token
            
        Raises:
            ValueError: Si el refresh token es inválido
        """
        from app.core.security import decode_refresh_token
        
        payload = decode_refresh_token(refresh_token)
        
        if not payload:
            raise ValueError("Refresh token inválido o expirado")
        
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Refresh token sin información de usuario")
        
        user = user_repository.get(db, user_id)
        if not user or not user.is_active:
            raise ValueError("Usuario no encontrado o inactivo")
        
        # Crear nuevo access token
        access_token = create_access_token(
            data={
                "sub": user.email,
                "user_id": user.id,
                "role": user.role.name if user.role else "unknown",
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }


login_service = LoginService()
