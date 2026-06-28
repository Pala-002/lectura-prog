"""
Servicio de recuperación de contraseña para SIET
"""

from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.models.models import User, PasswordReset
from app.repositories import user_repository
from app.core.security import get_password_hash, create_password_reset_token
from app.core.config import settings


class PasswordService:
    """Servicio para gestión de contraseñas y recuperación"""
    
    def request_password_reset(
        self,
        db: Session,
        email: str
    ) -> Optional[PasswordReset]:
        """
        Solicita un token para recuperación de contraseña.
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario
            
        Returns:
            Token de recuperación o None si el usuario no existe
        """
        # Buscar usuario por email
        user = user_repository.get_by_email(db, email)
        
        if not user:
            # No revelar si el usuario existe o no por seguridad
            return None
        
        # Invalidar tokens anteriores no usados
        old_tokens = db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.used == False
        ).all()
        
        for token in old_tokens:
            token.used = True
        
        # Crear nuevo token
        reset_token = create_password_reset_token(
            data={"user_id": user.id, "email": email}
        )
        
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token válido por 1 hora
        
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        
        db.add(password_reset)
        db.commit()
        db.refresh(password_reset)
        
        return password_reset
    
    def confirm_password_reset(
        self,
        db: Session,
        token: str,
        new_password: str
    ) -> bool:
        """
        Confirma el cambio de contraseña usando el token.
        
        Args:
            db: Sesión de base de datos
            token: Token de recuperación
            new_password: Nueva contraseña
            
        Returns:
            True si se cambió correctamente, False en caso contrario
        """
        # Buscar token
        password_reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.used == False
        ).first()
        
        if not password_reset:
            return False
        
        # Verificar expiración
        if password_reset.expires_at < datetime.utcnow():
            return False
        
        # Obtener usuario
        user = user_repository.get(db, password_reset.user_id)
        
        if not user or not user.is_active:
            return False
        
        # Validar fortaleza de contraseña (mínimo 8 caracteres)
        if len(new_password) < 8:
            return False
        
        # Actualizar contraseña
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Marcar token como usado
        password_reset.used = True
        
        db.commit()
        
        return True
    
    def change_password(
        self,
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> tuple[bool, str]:
        """
        Cambia la contraseña de un usuario autenticado.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            current_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            Tuple (éxito, mensaje de error)
        """
        user = user_repository.get(db, user_id)
        
        if not user:
            return False, "Usuario no encontrado"
        
        # Verificar contraseña actual
        from app.core.security import verify_password
        
        if not verify_password(current_password, user.password_hash):
            return False, "Contraseña actual incorrecta"
        
        # Validar fortaleza de nueva contraseña
        if len(new_password) < 8:
            return False, "La nueva contraseña debe tener al menos 8 caracteres"
        
        import re
        
        if not re.search(r'[A-Z]', new_password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        if not re.search(r'[a-z]', new_password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        if not re.search(r'\d', new_password):
            return False, "La contraseña debe contener al menos un número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', new_password):
            return False, "La contraseña debe contener al menos un carácter especial"
        
        # Actualizar contraseña
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True, ""


password_service = PasswordService()
