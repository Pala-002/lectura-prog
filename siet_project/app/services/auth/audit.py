"""
Servicio de auditoría para SIET
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import AuditLog
from app.repositories.base import BaseRepository


class AuditService:
    """Servicio para registro de eventos de auditoría"""
    
    def __init__(self):
        self.repository = BaseRepository(AuditLog)
    
    def log_action(
        self,
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        result: str = "success",
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Registra una acción en el log de auditoría.
        
        Args:
            db: Sesión de base de datos
            action: Acción realizada (login, logout, register, etc.)
            user_id: ID del usuario que realizó la acción
            module: Módulo donde se realizó la acción
            ip_address: Dirección IP del cliente
            user_agent: User agent del navegador
            result: Resultado de la acción (success, failure, error)
            details: Detalles adicionales en formato JSON
            
        Returns:
            Log de auditoría creado
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            details=details or {}
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    def log_login(
        self,
        db: Session,
        user_id: int,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Registra un intento de login"""
        return self.log_action(
            db=db,
            action="login",
            user_id=user_id,
            module="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            result="success" if success else "failure",
            details={"error": error_message} if not success and error_message else None
        )
    
    def log_logout(
        self,
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Registra un logout"""
        return self.log_action(
            db=db,
            action="logout",
            user_id=user_id,
            module="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            result="success"
        )
    
    def log_register(
        self,
        db: Session,
        user_id: int,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Registra un registro de usuario"""
        return self.log_action(
            db=db,
            action="register",
            user_id=user_id,
            module="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            result="success" if success else "failure",
            details={"error": error_message} if not success and error_message else None
        )
    
    def log_password_reset(
        self,
        db: Session,
        user_id: int,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Registra un intento de recuperación de contraseña"""
        return self.log_action(
            db=db,
            action="password_reset",
            user_id=user_id,
            module="auth",
            ip_address=ip_address,
            user_agent=user_agent,
            result="success" if success else "failure"
        )
    
    def log_profile_update(
        self,
        db: Session,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Registra una actualización de perfil"""
        return self.log_action(
            db=db,
            action="update_profile",
            user_id=user_id,
            module="users",
            ip_address=ip_address,
            user_agent=user_agent,
            result="success",
            details={"changes": changes} if changes else None
        )
    
    def get_user_logs(
        self,
        db: Session,
        user_id: int,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Obtiene los logs de auditoría de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de logs de auditoría
        """
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
    
    def get_module_logs(
        self,
        db: Session,
        module: str,
        limit: int = 100
    ) -> List[AuditLog]:
        """
        Obtiene los logs de auditoría de un módulo.
        
        Args:
            db: Sesión de base de datos
            module: Nombre del módulo
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de logs de auditoría
        """
        return db.query(AuditLog).filter(
            AuditLog.module == module
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()


audit_service = AuditService()
