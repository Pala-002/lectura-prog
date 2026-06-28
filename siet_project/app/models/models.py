"""
Modelos de base de datos para el sistema SIET
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Role(Base):
    """Tabla de roles de usuario"""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="role")


class User(Base):
    """Tabla de usuarios del sistema"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    role = relationship("Role", back_populates="users")
    consent = relationship("Consent", back_populates="user", uselist=False)
    sessions = relationship("Session", back_populates="user")
    redtic_answers = relationship("REDTICAnswer", back_populates="user")
    redtic_scores = relationship("REDTICScore", back_populates="user")
    stroop_results = relationship("StroopResult", back_populates="user")
    nback_results = relationship("NBackResult", back_populates="user")
    digitspan_results = relationship("DigitSpanResult", back_populates="user")
    trailmaking_results = relationship("TrailMakingResult", back_populates="user")
    crt_results = relationship("CRTResult", back_populates="user")
    learning_logs = relationship("LearningLog", back_populates="user")
    behavior_logs = relationship("BehaviorLog", back_populates="user")
    reports = relationship("Report", back_populates="user")


class Consent(Base):
    """Tabla de consentimiento informado"""
    
    __tablename__ = "consent"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    accepted = Column(Boolean, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    accepted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="consent")


class Session(Base):
    """Tabla de sesiones de evaluación"""
    
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    total_duration = Column(Integer)  # en segundos
    status = Column(String(20), default="active")  # active, completed, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")


class REDTICAnswer(Base):
    """Tabla de respuestas RED-TIC"""
    
    __tablename__ = "redtic_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    question_id = Column(Integer, nullable=False)
    dimension = Column(String(50), nullable=False)  # fatigue, anxiety, skepticism, inefficacy
    answer = Column(Integer, nullable=False)  # 1-5 Likert
    response_time = Column(Integer)  # en ms
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="redtic_answers")


class REDTICScore(Base):
    """Tabla de puntajes RED-TIC"""
    
    __tablename__ = "redtic_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    fatigue_score = Column(Float)
    anxiety_score = Column(Float)
    skepticism_score = Column(Float)
    inefficacy_score = Column(Float)
    global_score = Column(Float)
    level = Column(String(20))  # low, moderate, high, severe
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="redtic_scores")


class StroopResult(Base):
    """Tabla de resultados prueba Stroop"""
    
    __tablename__ = "stroop_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    total_stimuli = Column(Integer, default=20)
    congruent_correct = Column(Integer, default=0)
    congruent_incorrect = Column(Integer, default=0)
    incongruent_correct = Column(Integer, default=0)
    incongruent_incorrect = Column(Integer, default=0)
    avg_reaction_time = Column(Float)
    accuracy = Column(Float)
    interference_score = Column(Float)
    errors = Column(Integer, default=0)
    completion_time = Column(Integer)  # en ms
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="stroop_results")


class NBackResult(Base):
    """Tabla de resultados prueba N-Back"""
    
    __tablename__ = "nback_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    n_level = Column(Integer, default=2)
    total_trials = Column(Integer, default=20)
    hits = Column(Integer, default=0)
    misses = Column(Integer, default=0)
    false_alarms = Column(Integer, default=0)
    correct_rejections = Column(Integer, default=0)
    accuracy = Column(Float)
    avg_reaction_time = Column(Float)
    completion_time = Column(Integer)  # en ms
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="nback_results")


class DigitSpanResult(Base):
    """Tabla de resultados prueba Digit Span"""
    
    __tablename__ = "digitspan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    test_type = Column(String(10), nullable=False)  # forward, backward
    max_span = Column(Integer)
    total_errors = Column(Integer, default=0)
    total_time = Column(Integer)  # en ms
    levels_completed = Column(JSON)  # {level: [attempt1_result, attempt2_result]}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="digitspan_results")


class TrailMakingResult(Base):
    """Tabla de resultados prueba Trail Making"""
    
    __tablename__ = "trailmaking_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    version = Column(String(1), nullable=False)  # A, B
    completion_time = Column(Integer)  # en ms
    errors = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    sequence_traced = Column(JSON)  # secuencia de clicks
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="trailmaking_results")


class CRTResult(Base):
    """Tabla de resultados Cognitive Reflection Test"""
    
    __tablename__ = "crt_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    question_1_answer = Column(String(255))
    question_1_correct = Column(Boolean)
    question_1_time = Column(Integer)  # en ms
    question_2_answer = Column(String(255))
    question_2_correct = Column(Boolean)
    question_2_time = Column(Integer)  # en ms
    question_3_answer = Column(String(255))
    question_3_correct = Column(Boolean)
    question_3_time = Column(Integer)  # en ms
    total_correct = Column(Integer, default=0)
    total_time = Column(Integer)  # en ms
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="crt_results")


class LearningLog(Base):
    """Tabla de logs de Learning Analytics"""
    
    __tablename__ = "learning_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    event_type = Column(String(50), nullable=False)  # test_start, test_end, question_answer, etc.
    test_name = Column(String(50))
    question_id = Column(String(50))
    duration = Column(Integer)  # en ms
    clicks = Column(Integer, default=0)
    answer_changes = Column(Integer, default=0)
    event_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="learning_logs")


class BehaviorLog(Base):
    """Tabla de logs de Behavioral Analytics"""
    
    __tablename__ = "behavior_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    event_type = Column(String(50), nullable=False)  # mousemove, scroll, focus, blur, etc.
    x_coordinate = Column(Integer)
    y_coordinate = Column(Integer)
    scroll_position = Column(Integer)
    element_id = Column(String(100))
    page_url = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    behavior_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="behavior_logs")


class Report(Base):
    """Tabla de reportes generados"""
    
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # student, researcher, admin
    technostress_score = Column(Float)
    cognitive_score = Column(Float)
    behavior_score = Column(Float)
    overall_score = Column(Float)
    classification = Column(String(50))
    data = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="reports")


class AuditLog(Base):
    """Tabla de logs de auditoría"""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # login, logout, register, update_profile, etc.
    module = Column(String(50))  # auth, users, redtic, cognitive_tests, etc.
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    result = Column(String(20))  # success, failure, error
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", backref="audit_logs")


class PasswordReset(Base):
    """Tabla para recuperación de contraseñas"""
    
    __tablename__ = "password_reset"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="password_resets")
