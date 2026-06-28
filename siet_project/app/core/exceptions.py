"""
Excepciones personalizadas del sistema SIET
"""

from fastapi import HTTPException, status


class SIETException(HTTPException):
    """Excepción base para el sistema SIET"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Error en el sistema SIET",
        error_code: str = "SIET_ERROR"
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class UserNotFoundException(SIETException):
    """Usuario no encontrado"""
    
    def __init__(self, user_id: int = None, username: str = None):
        if user_id:
            detail = f"Usuario con ID {user_id} no encontrado"
        elif username:
            detail = f"Usuario '{username}' no encontrado"
        else:
            detail = "Usuario no encontrado"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="USER_NOT_FOUND"
        )


class InvalidCredentialsException(SIETException):
    """Credenciales inválidas"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            error_code="INVALID_CREDENTIALS"
        )


class ConsentNotGivenException(SIETException):
    """Consentimiento no otorgado"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debe aceptar el consentimiento informado para continuar",
            error_code="CONSENT_NOT_GIVEN"
        )


class TestAlreadyCompletedException(SIETException):
    """Prueba ya completada"""
    
    def __init__(self, test_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"La prueba {test_name} ya ha sido completada",
            error_code="TEST_ALREADY_COMPLETED"
        )


class DatabaseException(SIETException):
    """Error de base de datos"""
    
    def __init__(self, detail: str = "Error en la base de datos"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )
