"""
Endpoints de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserResponse, UserUpdate
from app.services.user_services import user_service
from app.services.auth import audit_service
from app.core.security import decode_access_token


router = APIRouter()


def get_current_user_from_token(request: Request, db: Session) -> User:
    """Obtiene el usuario actual del token JWT"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación"
        )
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin información de usuario"
        )
    
    user = user_service.get_user(db, user_id)
    return user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Obtener todos los usuarios (solo administradores)"""
    # Verificar permisos
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else ""
    payload = decode_access_token(token)
    role = payload.get("role", "") if payload else ""
    
    if role != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    users = db.query(User).filter(User.deleted_at == None).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)
):
    """Obtener usuario por ID"""
    # Verificar que el usuario solo pueda ver su propio perfil o sea admin
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else ""
    payload = decode_access_token(token)
    role = payload.get("role", "") if payload else ""
    current_user_id = payload.get("user_id") if payload else 0
    
    if role != "Administrador" and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes ver tu propio perfil"
        )
    
    user = user_service.get_user(db, user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Actualizar usuario"""
    # Obtener usuario actual
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else ""
    payload = decode_access_token(token)
    role = payload.get("role", "") if payload else ""
    current_user_id = payload.get("user_id") if payload else 0
    
    if role != "Administrador" and current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes editar tu propio perfil"
        )
    
    # No permitir modificar rol
    if hasattr(user_in, 'role_id') and user_in.role_id is not None and role != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes modificar tu rol"
        )
    
    user = user_service.update_user(db, user_id, user_in)
    
    # Registrar en auditoría
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    audit_service.log_profile_update(
        db=db,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        changes={"first_name": user_in.first_name, "last_name": user_in.last_name}
    )
    
    return user


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtener perfil del usuario actual"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación"
        )
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin información de usuario"
        )
    
    user = user_service.get_user(db, user_id)
    return user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Actualizar perfil del usuario actual"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación"
        )
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin información de usuario"
        )
    
    # No permitir modificar rol desde el perfil
    user = user_service.update_user(db, user_id, user_in)
    
    # Registrar en auditoría
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    audit_service.log_profile_update(
        db=db,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return user
