"""
Esquemas Pydantic para validación de datos
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== ROLES ====================

class RoleBase(BaseModel):
    """Esquema base para roles"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    """Esquema para crear rol"""
    pass


class RoleResponse(RoleBase):
    """Esquema de respuesta para rol"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== USUARIOS ====================

class UserBase(BaseModel):
    """Esquema base para usuarios"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    career: Optional[str] = Field(None, max_length=100)
    semester: Optional[int] = Field(None, ge=1, le=12)
    role_id: int


class UserCreate(UserBase):
    """Esquema para crear usuario"""
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    accept_terms: bool = False
    
    @classmethod
    def validate_passwords_match(cls, values):
        if values.get('password') != values.get('password_confirm'):
            raise ValueError('Las contraseñas no coinciden')
        return values
    
    @classmethod
    def validate_terms_accepted(cls, values):
        if not values.get('accept_terms'):
            raise ValueError('Debe aceptar los términos y condiciones')
        return values


class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    career: Optional[str] = Field(None, max_length=100)
    semester: Optional[int] = Field(None, ge=1, le=12)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Esquema de respuesta para usuario"""
    id: int
    uuid: str
    status: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Esquema para login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Esquema de token de acceso"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== CONSENTIMIENTO ====================

class ConsentBase(BaseModel):
    """Esquema base para consentimiento"""
    accepted: bool


class ConsentCreate(ConsentBase):
    """Esquema para crear consentimiento"""
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ConsentResponse(ConsentBase):
    """Esquema de respuesta para consentimiento"""
    id: int
    user_id: int
    accepted_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== SESIONES ====================

class SessionBase(BaseModel):
    """Esquema base para sesiones"""
    user_id: int


class SessionCreate(SessionBase):
    """Esquema para crear sesión"""
    pass


class SessionResponse(SessionBase):
    """Esquema de respuesta para sesión"""
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== RED-TIC ====================

class REDTICAnswerBase(BaseModel):
    """Esquema base para respuestas RED-TIC"""
    question_id: int
    dimension: str
    answer: int = Field(..., ge=1, le=5)
    response_time: Optional[int] = None


class REDTICAnswerCreate(REDTICAnswerBase):
    """Esquema para crear respuesta RED-TIC"""
    user_id: int
    session_id: Optional[int] = None


class REDTICAnswerResponse(REDTICAnswerBase):
    """Esquema de respuesta para respuesta RED-TIC"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class REDTICScoreBase(BaseModel):
    """Esquema base para puntajes RED-TIC"""
    fatigue_score: Optional[float] = None
    anxiety_score: Optional[float] = None
    skepticism_score: Optional[float] = None
    inefficacy_score: Optional[float] = None
    global_score: Optional[float] = None
    level: Optional[str] = None


class REDTICScoreCreate(REDTICScoreBase):
    """Esquema para crear puntaje RED-TIC"""
    user_id: int
    session_id: Optional[int] = None


class REDTICScoreResponse(REDTICScoreBase):
    """Esquema de respuesta para puntaje RED-TIC"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== STROOP ====================

class StroopResultBase(BaseModel):
    """Esquema base para resultados Stroop"""
    total_stimuli: int = 20
    congruent_correct: int = 0
    congruent_incorrect: int = 0
    incongruent_correct: int = 0
    incongruent_incorrect: int = 0
    avg_reaction_time: Optional[float] = None
    accuracy: Optional[float] = None
    interference_score: Optional[float] = None
    errors: int = 0
    completion_time: Optional[int] = None


class StroopResultCreate(StroopResultBase):
    """Esquema para crear resultado Stroop"""
    user_id: int
    session_id: Optional[int] = None


class StroopResultResponse(StroopResultBase):
    """Esquema de respuesta para resultado Stroop"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== N-BACK ====================

class NBackResultBase(BaseModel):
    """Esquema base para resultados N-Back"""
    n_level: int = 2
    total_trials: int = 20
    hits: int = 0
    misses: int = 0
    false_alarms: int = 0
    correct_rejections: int = 0
    accuracy: Optional[float] = None
    avg_reaction_time: Optional[float] = None
    completion_time: Optional[int] = None


class NBackResultCreate(NBackResultBase):
    """Esquema para crear resultado N-Back"""
    user_id: int
    session_id: Optional[int] = None


class NBackResultResponse(NBackResultBase):
    """Esquema de respuesta para resultado N-Back"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== DIGIT SPAN ====================

class DigitSpanResultBase(BaseModel):
    """Esquema base para resultados Digit Span"""
    test_type: str
    max_span: int
    total_errors: int = 0
    total_time: Optional[int] = None
    levels_completed: Optional[Dict[str, List[bool]]] = None


class DigitSpanResultCreate(DigitSpanResultBase):
    """Esquema para crear resultado Digit Span"""
    user_id: int
    session_id: Optional[int] = None


class DigitSpanResultResponse(DigitSpanResultBase):
    """Esquema de respuesta para resultado Digit Span"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== TRAIL MAKING ====================

class TrailMakingResultBase(BaseModel):
    """Esquema base para resultados Trail Making"""
    version: str
    completion_time: Optional[int] = None
    errors: int = 0
    completed: bool = False
    sequence_traced: Optional[Dict[str, Any]] = None


class TrailMakingResultCreate(TrailMakingResultBase):
    """Esquema para crear resultado Trail Making"""
    user_id: int
    session_id: Optional[int] = None


class TrailMakingResultResponse(TrailMakingResultBase):
    """Esquema de respuesta para resultado Trail Making"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== CRT ====================

class CRTResultBase(BaseModel):
    """Esquema base para resultados CRT"""
    question_1_answer: Optional[str] = None
    question_1_correct: Optional[bool] = None
    question_1_time: Optional[int] = None
    question_2_answer: Optional[str] = None
    question_2_correct: Optional[bool] = None
    question_2_time: Optional[int] = None
    question_3_answer: Optional[str] = None
    question_3_correct: Optional[bool] = None
    question_3_time: Optional[int] = None
    total_correct: int = 0
    total_time: Optional[int] = None


class CRTResultCreate(CRTResultBase):
    """Esquema para crear resultado CRT"""
    user_id: int
    session_id: Optional[int] = None


class CRTResultResponse(CRTResultBase):
    """Esquema de respuesta para resultado CRT"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== LEARNING ANALYTICS ====================

class LearningLogBase(BaseModel):
    """Esquema base para logs de learning analytics"""
    event_type: str
    test_name: Optional[str] = None
    question_id: Optional[str] = None
    duration: Optional[int] = None
    clicks: int = 0
    answer_changes: int = 0
    event_metadata: Optional[Dict[str, Any]] = None


class LearningLogCreate(LearningLogBase):
    """Esquema para crear log de learning analytics"""
    user_id: int
    session_id: Optional[int] = None


class LearningLogResponse(LearningLogBase):
    """Esquema de respuesta para log de learning analytics"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== BEHAVIORAL ANALYTICS ====================

class BehaviorLogBase(BaseModel):
    """Esquema base para logs de behavioral analytics"""
    event_type: str
    x_coordinate: Optional[int] = None
    y_coordinate: Optional[int] = None
    scroll_position: Optional[int] = None
    element_id: Optional[str] = None
    page_url: Optional[str] = None
    timestamp: Optional[datetime] = None
    behavior_metadata: Optional[Dict[str, Any]] = None


class BehaviorLogCreate(BehaviorLogBase):
    """Esquema para crear log de behavioral analytics"""
    user_id: int
    session_id: Optional[int] = None


class BehaviorLogResponse(BehaviorLogBase):
    """Esquema de respuesta para log de behavioral analytics"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== REPORTES ====================

class ReportBase(BaseModel):
    """Esquema base para reportes"""
    report_type: str
    technostress_score: Optional[float] = None
    cognitive_score: Optional[float] = None
    behavior_score: Optional[float] = None
    overall_score: Optional[float] = None
    classification: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ReportCreate(ReportBase):
    """Esquema para crear reporte"""
    user_id: int


class ReportResponse(ReportBase):
    """Esquema de respuesta para reporte"""
    id: int
    user_id: int
    generated_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== DASHBOARD ====================

class DashboardStudentResponse(BaseModel):
    """Esquema de dashboard para estudiante"""
    technostress_level: str
    technostress_scores: Dict[str, float]
    cognitive_results: Dict[str, Any]
    indicators: Dict[str, float]
    history: List[ReportResponse]
    recommendations: List[str]


class DashboardResearcherResponse(BaseModel):
    """Esquema de dashboard para investigador"""
    averages: Dict[str, float]
    distributions: Dict[str, Any]
    comparisons: Dict[str, Any]
    total_users: int
    total_sessions: int


class DashboardAdminResponse(BaseModel):
    """Esquema de dashboard para administrador"""
    total_users: int
    total_admins: int
    total_researchers: int
    total_students: int
    active_sessions: int
    system_status: str


# ==================== AUDITORÍA ====================

class AuditLogBase(BaseModel):
    """Esquema base para logs de auditoría"""
    action: str
    module: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    result: str
    details: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    """Esquema para crear log de auditoría"""
    user_id: Optional[int] = None


class AuditLogResponse(AuditLogBase):
    """Esquema de respuesta para log de auditoría"""
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== RECUPERACIÓN DE CONTRASEÑA ====================

class PasswordResetRequest(BaseModel):
    """Esquema para solicitar recuperación de contraseña"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Esquema para confirmar recuperación de contraseña"""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @classmethod
    def validate_password_strength(cls, values):
        password = values.get('new_password')
        if len(password) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(c.isupper() for c in password):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(c.islower() for c in password):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(c.isdigit() for c in password):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(c in '!@#$%^&*(),.?":{}|<>_\\-+=[]\\\\;\'`~' for c in password):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return values


class PasswordResetToken(BaseModel):
    """Esquema de token de recuperación"""
    token: str
    expires_at: datetime
    used: bool
    
    model_config = ConfigDict(from_attributes=True)
