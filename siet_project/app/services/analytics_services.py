"""
Servicios de Analytics para el Motor Analítico SIET
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.models import (
    REDTICScore,
    StroopResult,
    NBackResult,
    DigitSpanResult,
    TrailMakingResult,
    CRTResult,
    LearningLog,
    BehaviorLog,
    Report
)
from app.core.config import settings


class AnalyticsEngine:
    """
    Motor Analítico Basado en Reglas (Rule-Based Analytics Engine)
    
    Pipeline:
    1. Captura
    2. Validación
    3. Normalización
    4. Indicadores
    5. Clasificación
    6. Dashboard
    """
    
    def __init__(self):
        # Ponderaciones configurables
        self.weight_technostress = settings.WEIGHT_TECHNOSTRESS
        self.weight_cognitive = settings.WEIGHT_COGNITIVE
        self.weight_behavior = settings.WEIGHT_BEHAVIOR
    
    def calculate_technostress_score(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Calcula puntaje de tecnoestrés basado en RED-TIC.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Diccionario con puntajes y nivel
        """
        latest_score = db.query(REDTICScore).filter(
            REDTICScore.user_id == user_id
        ).order_by(REDTICScore.created_at.desc()).first()
        
        if not latest_score:
            return {
                "global_score": 0,
                "dimension_scores": {},
                "level": "unknown"
            }
        
        dimension_scores = {
            "fatigue": latest_score.fatigue_score or 0,
            "anxiety": latest_score.anxiety_score or 0,
            "skepticism": latest_score.skepticism_score or 0,
            "inefficacy": latest_score.inefficacy_score or 0
        }
        
        # Normalizar a escala 0-100
        normalized_global = (latest_score.global_score or 0) / 5 * 100
        
        return {
            "global_score": normalized_global,
            "dimension_scores": {k: v / 5 * 100 for k, v in dimension_scores.items()},
            "level": latest_score.level or "unknown"
        }
    
    def calculate_cognitive_score(
        self,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Calcula puntaje cognitivo combinado.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Diccionario con puntajes por prueba
        """
        scores = {}
        
        # Stroop
        stroop = db.query(StroopResult).filter(
            StroopResult.user_id == user_id
        ).order_by(StroopResult.created_at.desc()).first()
        
        if stroop:
            scores["stroop"] = {
                "accuracy": stroop.accuracy or 0,
                "interference": stroop.interference_score or 0,
                "rt": stroop.avg_reaction_time or 0
            }
        
        # N-Back
        nback = db.query(NBackResult).filter(
            NBackResult.user_id == user_id
        ).order_by(NBackResult.created_at.desc()).first()
        
        if nback:
            scores["nback"] = {
                "accuracy": nback.accuracy or 0,
                "hits": nback.hits or 0,
                "false_alarms": nback.false_alarms or 0,
                "rt": nback.avg_reaction_time or 0
            }
        
        # Digit Span
        digitspan_forward = db.query(DigitSpanResult).filter(
            DigitSpanResult.user_id == user_id,
            DigitSpanResult.test_type == "forward"
        ).order_by(DigitSpanResult.created_at.desc()).first()
        
        digitspan_backward = db.query(DigitSpanResult).filter(
            DigitSpanResult.user_id == user_id,
            DigitSpanResult.test_type == "backward"
        ).order_by(DigitSpanResult.created_at.desc()).first()
        
        if digitspan_forward or digitspan_backward:
            forward_span = digitspan_forward.max_span if digitspan_forward else 0
            backward_span = digitspan_backward.max_span if digitspan_backward else 0
            scores["digitspan"] = {
                "forward_span": forward_span,
                "backward_span": backward_span,
                "total_span": forward_span + backward_span
            }
        
        # Trail Making
        trail_a = db.query(TrailMakingResult).filter(
            TrailMakingResult.user_id == user_id,
            TrailMakingResult.version == "A"
        ).order_by(TrailMakingResult.created_at.desc()).first()
        
        trail_b = db.query(TrailMakingResult).filter(
            TrailMakingResult.user_id == user_id,
            TrailMakingResult.version == "B"
        ).order_by(TrailMakingResult.created_at.desc()).first()
        
        if trail_a or trail_b:
            scores["trailmaking"] = {
                "time_a": trail_a.completion_time if trail_a else 0,
                "time_b": trail_b.completion_time if trail_b else 0,
                "errors_a": trail_a.errors if trail_a else 0,
                "errors_b": trail_b.errors if trail_b else 0
            }
        
        # CRT
        crt = db.query(CRTResult).filter(
            CRTResult.user_id == user_id
        ).order_by(CRTResult.created_at.desc()).first()
        
        if crt:
            scores["crt"] = {
                "correct": crt.total_correct or 0,
                "total": 3,
                "percentage": (crt.total_correct or 0) / 3 * 100
            }
        
        # Calcular score cognitivo global (promedio ponderado)
        cognitive_components = []
        
        if "stroop" in scores:
            cognitive_components.append(scores["stroop"]["accuracy"])
        
        if "nback" in scores:
            cognitive_components.append(scores["nback"]["accuracy"])
        
        if "digitspan" in scores:
            # Normalizar span (max teórico 9+9=18)
            normalized_span = scores["digitspan"]["total_span"] / 18 * 100
            cognitive_components.append(normalized_span)
        
        if "crt" in scores:
            cognitive_components.append(scores["crt"]["percentage"])
        
        global_cognitive = (
            sum(cognitive_components) / len(cognitive_components) 
            if cognitive_components else 0
        )
        
        return {
            "tests": scores,
            "global_score": global_cognitive
        }
    
    def calculate_behavior_score(
        self,
        db: Session,
        user_id: int,
        session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcula puntaje de comportamiento.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            session_id: ID de sesión opcional
            
        Returns:
            Diccionario con indicadores de comportamiento
        """
        query = db.query(BehaviorLog).filter(
            BehaviorLog.user_id == user_id
        )
        
        if session_id:
            query = query.filter(BehaviorLog.session_id == session_id)
        
        behavior_logs = query.all()
        
        # Contar eventos por tipo
        event_counts = {}
        for log in behavior_logs:
            event_type = log.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Calcular indicadores
        total_events = len(behavior_logs)
        
        # Eventos de distracción
        distraction_events = (
            event_counts.get("blur", 0) +
            event_counts.get("visibilitychange", 0) +
            event_counts.get("tab_change", 0)
        )
        
        # Eventos de interacción
        interaction_events = (
            event_counts.get("mousemove", 0) +
            event_counts.get("click", 0) +
            event_counts.get("scroll", 0)
        )
        
        # Idle time
        idle_events = event_counts.get("idle", 0)
        
        # Calcular score (más interacción = mejor, más distracción = peor)
        if total_events > 0:
            engagement_ratio = interaction_events / total_events
            distraction_ratio = distraction_events / total_events
            
            behavior_score = (engagement_ratio * 70) + ((1 - distraction_ratio) * 30)
        else:
            behavior_score = 50  # Default neutral
        
        return {
            "total_events": total_events,
            "event_counts": event_counts,
            "distraction_events": distraction_events,
            "interaction_events": interaction_events,
            "idle_events": idle_events,
            "global_score": min(100, max(0, behavior_score))
        }
    
    def calculate_overall_score(
        self,
        technostress_score: float,
        cognitive_score: float,
        behavior_score: float
    ) -> Dict[str, Any]:
        """
        Calcula puntaje overall combinado.
        
        Args:
            technostress_score: Puntaje de tecnoestrés (0-100)
            cognitive_score: Puntaje cognitivo (0-100)
            behavior_score: Puntaje de comportamiento (0-100)
            
        Returns:
            Diccionario con puntaje overall y clasificación
        """
        # Tecnoestrés: menor es mejor (invertir para cálculo)
        inverted_technostress = 100 - technostress_score
        
        # Ponderar componentes
        overall = (
            inverted_technostress * self.weight_technostress +
            cognitive_score * self.weight_cognitive +
            behavior_score * self.weight_behavior
        )
        
        # Clasificar
        if overall >= 80:
            classification = "optimal"
        elif overall >= 60:
            classification = "acceptable"
        elif overall >= 40:
            classification = "moderate_risk"
        elif overall >= 20:
            classification = "high_risk"
        else:
            classification = "critical"
        
        return {
            "overall_score": overall,
            "technostress_component": inverted_technostress * self.weight_technostress,
            "cognitive_component": cognitive_score * self.weight_cognitive,
            "behavior_component": behavior_score * self.weight_behavior,
            "classification": classification
        }
    
    def generate_report(
        self,
        db: Session,
        user_id: int,
        session_id: Optional[int] = None
    ) -> Report:
        """
        Genera reporte completo del usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            session_id: ID de sesión opcional
            
        Returns:
            Reporte generado
        """
        # Calcular todos los scores
        technostress_data = self.calculate_technostress_score(db, user_id)
        cognitive_data = self.calculate_cognitive_score(db, user_id)
        behavior_data = self.calculate_behavior_score(db, user_id, session_id)
        
        overall_data = self.calculate_overall_score(
            technostress_data["global_score"],
            cognitive_data["global_score"],
            behavior_data["global_score"]
        )
        
        # Crear reporte
        report_data = {
            "technostress": technostress_data,
            "cognitive": cognitive_data,
            "behavior": behavior_data,
            "overall": overall_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        report = Report(
            user_id=user_id,
            report_type="student",
            technostress_score=technostress_data["global_score"],
            cognitive_score=cognitive_data["global_score"],
            behavior_score=behavior_data["global_score"],
            overall_score=overall_data["overall_score"],
            classification=overall_data["classification"],
            data=report_data
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return report
    
    def get_recommendations(
        self,
        technostress_level: str,
        cognitive_score: float,
        behavior_score: float
    ) -> List[str]:
        """
        Genera recomendaciones basadas en resultados.
        
        Args:
            technostress_level: Nivel de tecnoestrés
            cognitive_score: Puntaje cognitivo
            behavior_score: Puntaje de comportamiento
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones por tecnoestrés
        if technostress_level in ["high", "severe"]:
            recommendations.append(
                "Se recomienda realizar pausas activas cada 45-60 minutos de uso tecnológico."
            )
            recommendations.append(
                "Considere técnicas de gestión del estrés como mindfulness o respiración profunda."
            )
        
        if technostress_level == "severe":
            recommendations.append(
                "Se sugiere consultar con un especialista en salud mental digital."
            )
        
        # Recomendaciones cognitivas
        if cognitive_score < 50:
            recommendations.append(
                "Realice ejercicios de entrenamiento cognitivo regularmente."
            )
        
        # Recomendaciones de comportamiento
        if behavior_score < 50:
            recommendations.append(
                "Minimice las distracciones durante las tareas digitales."
            )
            recommendations.append(
                "Establezca períodos de trabajo sin interrupciones."
            )
        
        if not recommendations:
            recommendations.append(
                "Mantenga hábitos saludables de uso tecnológico."
            )
            recommendations.append(
                "Continúe con prácticas de bienestar digital."
            )
        
        return recommendations


analytics_engine = AnalyticsEngine()
