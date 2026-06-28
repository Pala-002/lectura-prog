"""
Servicio de registro de usuarios para SIET
"""

from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import re

from app.models.models import User, Role
from app.schemas.schemas import UserCreate
from app.repositories import user_repository, role_repository
from app.core.security import get_password_hash


class RegisterService:
    """Servicio para registro de nuevos usuarios"""
    
    # Contraseñas comunes no permitidas
    COMMON_PASSWORDS = {
        '123456', 'password', 'qwerty', '123456789', '12345678', 
        '12345', '111111', '1234567', 'sunshine', 'iloveyou',
        'admin', 'letmein', 'welcome', 'monkey', 'dragon'
    }
    
    def validate_password_strength(self, password: str, user_data: dict = None) -> tuple[bool, str]:
        """
        Valida la fortaleza de la contraseña.
        
        Args:
            password: Contraseña a validar
            user_data: Datos del usuario (para verificar que no esté en la contraseña)
            
        Returns:
            Tuple (es_valida, mensaje_error)
        """
        # Longitud mínima
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        # Verificar mayúsculas
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        # Verificar minúsculas
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe contener al menos una letra minúscula"
        
        # Verificar números
        if not re.search(r'\d', password):
            return False, "La contraseña debe contener al menos un número"
        
        # Verificar caracteres especiales
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
            return False, "La contraseña debe contener al menos un carácter especial"
        
        # Verificar contraseñas comunes
        if password.lower() in self.COMMON_PASSWORDS:
            return False, "La contraseña es demasiado común. Por favor elija una más segura"
        
        # Verificar que no contenga el nombre o apellido
        if user_data:
            first_name = user_data.get('first_name', '').lower()
            last_name = user_data.get('last_name', '').lower()
            email = user_data.get('email', '').lower()
            
            if first_name and first_name in password.lower():
                return False, "La contraseña no puede contener su nombre"
            if last_name and last_name in password.lower():
                return False, "La contraseña no puede contener su apellido"
            if email and email.split('@')[0] in password.lower():
                return False, "La contraseña no puede contener su correo electrónico"
        
        return True, ""
    
    def register(
        self,
        db: Session,
        user_in: UserCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            db: Sesión de base de datos
            user_in: Datos del usuario a registrar
            ip_address: Dirección IP del cliente
            user_agent: User agent del navegador
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar fortaleza de contraseña
        user_data = {
            'first_name': user_in.first_name,
            'last_name': user_in.last_name,
            'email': user_in.email
        }
        is_valid, error_msg = self.validate_password_strength(user_in.password, user_data)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Verificar que el rol existe (por defecto Estudiante = 3)
        role_id = user_in.role_id if user_in.role_id else 3
        role = role_repository.get(db, role_id)
        if not role:
            # Intentar obtener rol por nombre si no se encontró por ID
            role = role_repository.get_by_name(db, "Estudiante")
            if not role:
                raise ValueError("El rol especificado no existe")
            role_id = role.id
        
        # Verificar que el email no exista
        existing_email = user_repository.get_by_email(db, user_in.email)
        if existing_email:
            raise ValueError("El email ya está registrado")
        
        # Crear usuario
        user_data = {
            "first_name": user_in.first_name,
            "last_name": user_in.last_name,
            "email": user_in.email,
            "password_hash": get_password_hash(user_in.password),
            "role_id": role_id,
            "career": user_in.career,
            "semester": user_in.semester,
            "is_active": True,
            "status": "active"
        }
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user


register_service = RegisterService()
