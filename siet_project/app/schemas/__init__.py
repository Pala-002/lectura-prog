"""
Esquemas del sistema SIET
"""

from app.schemas.schemas import (
    # Roles
    RoleBase,
    RoleCreate,
    RoleResponse,
    # Usuarios
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    # Consentimiento
    ConsentBase,
    ConsentCreate,
    ConsentResponse,
    # Sesiones
    SessionBase,
    SessionCreate,
    SessionResponse,
    # RED-TIC
    REDTICAnswerBase,
    REDTICAnswerCreate,
    REDTICAnswerResponse,
    REDTICScoreBase,
    REDTICScoreCreate,
    REDTICScoreResponse,
    # Stroop
    StroopResultBase,
    StroopResultCreate,
    StroopResultResponse,
    # N-Back
    NBackResultBase,
    NBackResultCreate,
    NBackResultResponse,
    # Digit Span
    DigitSpanResultBase,
    DigitSpanResultCreate,
    DigitSpanResultResponse,
    # Trail Making
    TrailMakingResultBase,
    TrailMakingResultCreate,
    TrailMakingResultResponse,
    # CRT
    CRTResultBase,
    CRTResultCreate,
    CRTResultResponse,
    # Learning Analytics
    LearningLogBase,
    LearningLogCreate,
    LearningLogResponse,
    # Behavioral Analytics
    BehaviorLogBase,
    BehaviorLogCreate,
    BehaviorLogResponse,
    # Reportes
    ReportBase,
    ReportCreate,
    ReportResponse,
    # Dashboard
    DashboardStudentResponse,
    DashboardResearcherResponse,
    DashboardAdminResponse
)

__all__ = [
    # Roles
    "RoleBase",
    "RoleCreate",
    "RoleResponse",
    # Usuarios
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    # Consentimiento
    "ConsentBase",
    "ConsentCreate",
    "ConsentResponse",
    # Sesiones
    "SessionBase",
    "SessionCreate",
    "SessionResponse",
    # RED-TIC
    "REDTICAnswerBase",
    "REDTICAnswerCreate",
    "REDTICAnswerResponse",
    "REDTICScoreBase",
    "REDTICScoreCreate",
    "REDTICScoreResponse",
    # Stroop
    "StroopResultBase",
    "StroopResultCreate",
    "StroopResultResponse",
    # N-Back
    "NBackResultBase",
    "NBackResultCreate",
    "NBackResultResponse",
    # Digit Span
    "DigitSpanResultBase",
    "DigitSpanResultCreate",
    "DigitSpanResultResponse",
    # Trail Making
    "TrailMakingResultBase",
    "TrailMakingResultCreate",
    "TrailMakingResultResponse",
    # CRT
    "CRTResultBase",
    "CRTResultCreate",
    "CRTResultResponse",
    # Learning Analytics
    "LearningLogBase",
    "LearningLogCreate",
    "LearningLogResponse",
    # Behavioral Analytics
    "BehaviorLogBase",
    "BehaviorLogCreate",
    "BehaviorLogResponse",
    # Reportes
    "ReportBase",
    "ReportCreate",
    "ReportResponse",
    # Dashboard
    "DashboardStudentResponse",
    "DashboardResearcherResponse",
    "DashboardAdminResponse"
]
