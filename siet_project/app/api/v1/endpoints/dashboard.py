"""
Endpoints de Dashboard
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.schemas.schemas import (
    DashboardStudentResponse,
    DashboardResearcherResponse,
    DashboardAdminResponse,
    ReportResponse
)
from app.services.analytics_services import analytics_engine
from app.models.models import User, Role, Session as SessionModel, Report


router = APIRouter()


# ==================== STUDENT DASHBOARD ====================

@router.get("/student/{user_id}", response_model=DashboardStudentResponse)
async def get_student_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Obtener dashboard completo para estudiante"""
    # Obtener análisis de tecnoestrés
    technostress_data = analytics_engine.calculate_technostress_score(db, user_id)
    
    # Obtener análisis cognitivo
    cognitive_data = analytics_engine.calculate_cognitive_score(db, user_id)
    
    # Obtener análisis de comportamiento
    behavior_data = analytics_engine.calculate_behavior_score(db, user_id)
    
    # Calcular overall score
    overall_data = analytics_engine.calculate_overall_score(
        technostress_data["global_score"],
        cognitive_data["global_score"],
        behavior_data["global_score"]
    )
    
    # Obtener historial de reportes
    reports = db.query(Report).filter(
        Report.user_id == user_id
    ).order_by(Report.created_at.desc()).limit(10).all()
    
    # Generar recomendaciones
    recommendations = analytics_engine.get_recommendations(
        technostress_data.get("level", "unknown"),
        cognitive_data["global_score"],
        behavior_data["global_score"]
    )
    
    return {
        "technostress_level": technostress_data.get("level", "unknown"),
        "technostress_scores": technostress_data.get("dimension_scores", {}),
        "cognitive_results": cognitive_data.get("tests", {}),
        "indicators": {
            "technostress_global": technostress_data["global_score"],
            "cognitive_global": cognitive_data["global_score"],
            "behavior_global": behavior_data["global_score"],
            "overall": overall_data["overall_score"]
        },
        "history": reports,
        "recommendations": recommendations
    }


# ==================== RESEARCHER DASHBOARD ====================

@router.get("/researcher", response_model=DashboardResearcherResponse)
async def get_researcher_dashboard(db: Session = Depends(get_db)):
    """Obtener dashboard para investigador con estadísticas agregadas"""
    # Contar usuarios totales
    total_users = db.query(User).count()
    
    # Contar sesiones totales
    total_sessions = db.query(SessionModel).count()
    
    # Calcular promedios de tecnoestrés
    from sqlalchemy import func
    
    avg_technostress = db.query(func.avg(Report.overall_score)).filter(
        Report.report_type == "student"
    ).scalar() or 0
    
    # Distribución por nivel de tecnoestrés
    stress_distribution = {
        "low": db.query(User).join(Report).filter(
            Report.classification == "optimal"
        ).distinct().count(),
        "moderate": db.query(User).join(Report).filter(
            Report.classification == "acceptable"
        ).distinct().count(),
        "high": db.query(User).join(Report).filter(
            Report.classification.in_(["moderate_risk", "high_risk"])
        ).distinct().count(),
        "critical": db.query(User).join(Report).filter(
            Report.classification == "critical"
        ).distinct().count()
    }
    
    # Promedios por prueba cognitiva
    from app.models.models import StroopResult, NBackResult, CRTResult
    
    avg_stroop_accuracy = db.query(func.avg(StroopResult.accuracy)).scalar() or 0
    avg_nback_accuracy = db.query(func.avg(NBackResult.accuracy)).scalar() or 0
    avg_crt_correct = db.query(func.avg(CRTResult.total_correct)).scalar() or 0
    
    averages = {
        "technostress_overall": avg_technostress,
        "stroop_accuracy": avg_stroop_accuracy,
        "nback_accuracy": avg_nback_accuracy,
        "crt_correct_avg": avg_crt_correct
    }
    
    distributions = {
        "stress_levels": stress_distribution,
        "total_users": total_users
    }
    
    comparisons = {
        "by_role": {},
        "by_date": {}
    }
    
    return {
        "averages": averages,
        "distributions": distributions,
        "comparisons": comparisons,
        "total_users": total_users,
        "total_sessions": total_sessions
    }


# ==================== ADMIN DASHBOARD ====================

@router.get("/admin", response_model=DashboardAdminResponse)
async def get_admin_dashboard(db: Session = Depends(get_db)):
    """Obtener dashboard para administrador"""
    # Contar usuarios por rol
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    researcher_role = db.query(Role).filter(Role.name == "researcher").first()
    student_role = db.query(Role).filter(Role.name == "student").first()
    
    total_admins = db.query(User).filter(
        User.role_id == admin_role.id if admin_role else 0
    ).count()
    
    total_researchers = db.query(User).filter(
        User.role_id == researcher_role.id if researcher_role else 0
    ).count()
    
    total_students = db.query(User).filter(
        User.role_id == student_role.id if student_role else 0
    ).count()
    
    total_users = total_admins + total_researchers + total_students
    
    # Sesiones activas
    active_sessions = db.query(SessionModel).filter(
        SessionModel.status == "active"
    ).count()
    
    # Estado del sistema
    system_status = "operational"
    
    return {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_researchers": total_researchers,
        "total_students": total_students,
        "active_sessions": active_sessions,
        "system_status": system_status
    }


# ==================== REPORTS ====================

@router.post("/report/generate/{user_id}")
async def generate_report(user_id: int, db: Session = Depends(get_db)):
    """Generar reporte completo para un usuario"""
    report = analytics_engine.generate_report(db, user_id)
    return {"report_id": report.id, "generated_at": report.generated_at}


@router.get("/reports/user/{user_id}", response_model=List[ReportResponse])
async def get_user_reports(user_id: int, db: Session = Depends(get_db)):
    """Obtener todos los reportes de un usuario"""
    reports = db.query(Report).filter(
        Report.user_id == user_id
    ).order_by(Report.created_at.desc()).all()
    
    return reports
