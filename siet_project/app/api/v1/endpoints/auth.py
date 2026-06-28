"""
Endpoints de autenticación
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any

from app.db.database import get_db
from app.schemas.schemas import UserCreate, UserResponse, UserLogin, PasswordResetRequest, PasswordResetConfirm
from app.services.auth import login_service, register_service, password_service, audit_service
from app.core.config import settings


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    try:
        # Obtener IP y user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Registrar usuario
        user = register_service.register(
            db=db,
            user_in=user_in,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Registrar en auditoría
        audit_service.log_register(
            db=db,
            user_id=user.id,
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return user
    except ValueError as e:
        # Registrar fallo en auditoría
        audit_service.log_register(
            db=db,
            user_id=None,
            success=False,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            error_message=str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login de usuario"""
    # Obtener IP y user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        result = login_service.login(
            db=db,
            username=login_data.username,
            password=login_data.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Registrar login exitoso en auditoría
        audit_service.log_login(
            db=db,
            user_id=result["user"]["id"],
            success=True,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return result
    except ValueError as e:
        # Buscar usuario para registrar en auditoría (si existe)
        user = user_repository.get_by_username(db, login_data.username)
        if not user:
            user = user_repository.get_by_email(db, login_data.username)
        
        # Registrar login fallido en auditoría
        audit_service.log_login(
            db=db,
            user_id=user.id if user else None,
            success=False,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/logout")
async def logout(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db)
):
    """Cerrar sesión"""
    try:
        # Obtener usuario del token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se proporcionó token de autenticación"
            )
        
        from app.core.security import decode_access_token
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user_id = payload.get("user_id")
        
        # Cerrar sesión
        success = login_service.logout(db=db, session_id=session_id, user_id=user_id)
        
        if success:
            # Registrar logout en auditoría
            audit_service.log_logout(
                db=db,
                user_id=user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
            
            return {"message": "Sesión cerrada correctamente"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo cerrar la sesión"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Renovar token de acceso"""
    try:
        result = login_service.refresh_token(db=db, refresh_token=refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Obtener usuario actual"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación"
        )
    
    from app.core.security import decode_access_token
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
    
    from app.repositories import user_repository
    user = user_repository.get(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user


@router.post("/forgot-password")
async def forgot_password(
    reset_request: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Solicitar recuperación de contraseña"""
    # Obtener IP y user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Solicitar reset (no revelamos si el usuario existe)
    password_reset = password_service.request_password_reset(
        db=db,
        email=reset_request.email
    )
    
    # En producción, aquí se enviaría un email con el token
    # Para este prototipo, retornamos el token (solo para desarrollo)
    if password_reset and settings.DEBUG:
        return {
            "message": "Se ha enviado un enlace de recuperación a tu correo",
            "token": password_reset.token,  # Solo en modo DEBUG
            "expires_at": password_reset.expires_at
        }
    else:
        return {
            "message": "Si el correo está registrado, recibirás un enlace de recuperación"
        }


@router.post("/reset-password")
async def reset_password(
    reset_confirm: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Restablecer contraseña con token"""
    # Obtener IP y user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Confirmar reset
    from app.core.security import decode_password_reset_token
    payload = decode_password_reset_token(reset_confirm.token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    user_id = payload.get("user_id")
    
    success = password_service.confirm_password_reset(
        db=db,
        token=reset_confirm.token,
        new_password=reset_confirm.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo restablecer la contraseña. El token puede haber expirado."
        )
    
    # Registrar en auditoría
    audit_service.log_password_reset(
        db=db,
        user_id=user_id,
        success=True,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return {"message": "Contraseña restablecida correctamente"}
