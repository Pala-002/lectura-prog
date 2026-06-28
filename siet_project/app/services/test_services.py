"""
Servicios para pruebas cognitivas y RED-TIC
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import (
    REDTICAnswer,
    REDTICScore,
    StroopResult,
    NBackResult,
    DigitSpanResult,
    TrailMakingResult,
    CRTResult
)
from app.schemas.schemas import (
    REDTICAnswerCreate,
    StroopResultCreate,
    NBackResultCreate,
    DigitSpanResultCreate,
    TrailMakingResultCreate,
    CRTResultCreate
)


# ==================== RED-TIC SERVICE ====================

class REDTICService:
    """Servicio para evaluación RED-TIC"""
    
    # Preguntas RED-TIC por dimensión
    QUESTIONS = {
        "fatigue": list(range(1, 6)),  # Questions 1-5
        "anxiety": list(range(6, 11)),  # Questions 6-10
        "skepticism": list(range(11, 16)),  # Questions 11-15
        "inefficacy": list(range(16, 21))  # Questions 16-20
    }
    
    def calculate_dimension_score(
        self,
        answers: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calcula puntajes por dimensión.
        
        Args:
            answers: Lista de respuestas con question_id y answer
            
        Returns:
            Diccionario con puntajes por dimensión
        """
        scores = {
            "fatigue": 0.0,
            "anxiety": 0.0,
            "skepticism": 0.0,
            "inefficacy": 0.0
        }
        
        for answer in answers:
            question_id = answer.get("question_id")
            value = answer.get("answer", 0)
            
            for dimension, questions in self.QUESTIONS.items():
                if question_id in questions:
                    scores[dimension] += value
                    break
        
        # Promediar (5 preguntas por dimensión)
        for dimension in scores:
            scores[dimension] = scores[dimension] / 5
        
        return scores
    
    def calculate_global_score(
        self,
        dimension_scores: Dict[str, float]
    ) -> float:
        """
        Calcula puntaje global.
        
        Args:
            dimension_scores: Puntajes por dimensión
            
        Returns:
            Puntaje global
        """
        return sum(dimension_scores.values()) / len(dimension_scores)
    
    def classify_level(self, global_score: float) -> str:
        """
        Clasifica nivel de tecnoestrés.
        
        Args:
            global_score: Puntaje global (1-5)
            
        Returns:
            Nivel clasificado
        """
        if global_score <= 2.0:
            return "low"
        elif global_score <= 3.0:
            return "moderate"
        elif global_score <= 4.0:
            return "high"
        else:
            return "severe"
    
    def save_results(
        self,
        db: Session,
        user_id: int,
        session_id: Optional[int],
        answers: List[REDTICAnswerCreate]
    ) -> REDTICScore:
        """
        Guarda resultados RED-TIC.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            session_id: ID de la sesión
            answers: Respuestas del usuario
            
        Returns:
            Puntaje calculado
        """
        # Guardar respuestas
        for answer in answers:
            db_answer = REDTICAnswer(
                user_id=user_id,
                session_id=session_id,
                question_id=answer.question_id,
                dimension=answer.dimension,
                answer=answer.answer,
                response_time=answer.response_time
            )
            db.add(db_answer)
        
        db.commit()
        
        # Calcular puntajes
        answers_data = [a.dict() for a in answers]
        dimension_scores = self.calculate_dimension_score(answers_data)
        global_score = self.calculate_global_score(dimension_scores)
        level = self.classify_level(global_score)
        
        # Guardar puntaje
        score = REDTICScore(
            user_id=user_id,
            session_id=session_id,
            fatigue_score=dimension_scores["fatigue"],
            anxiety_score=dimension_scores["anxiety"],
            skepticism_score=dimension_scores["skepticism"],
            inefficacy_score=dimension_scores["inefficacy"],
            global_score=global_score,
            level=level
        )
        
        db.add(score)
        db.commit()
        db.refresh(score)
        
        return score


# ==================== COGNITIVE TESTS SERVICE ====================

class CognitiveTestsService:
    """Servicio para pruebas cognitivas"""
    
    def save_stroop_result(
        self,
        db: Session,
        result_in: StroopResultCreate
    ) -> StroopResult:
        """Guarda resultado de prueba Stroop"""
        
        # Calcular métricas adicionales
        total_correct = (
            result_in.congruent_correct + 
            result_in.incongruent_correct
        )
        total_incorrect = (
            result_in.congruent_incorrect + 
            result_in.incongruent_incorrect
        )
        total = total_correct + total_incorrect
        
        accuracy = (total_correct / total * 100) if total > 0 else 0
        
        # Calcular interference score
        if result_in.incongruent_correct > 0 and result_in.avg_reaction_time:
            # Interference = RT_incongruent - RT_congruent
            # Simplificado: diferencia porcentual esperada
            interference_score = (
                (result_in.incongruent_incorrect - result_in.congruent_incorrect) 
                / max(total, 1) * 100
            )
        else:
            interference_score = 0
        
        result = StroopResult(
            user_id=result_in.user_id,
            session_id=result_in.session_id,
            total_stimuli=result_in.total_stimuli,
            congruent_correct=result_in.congruent_correct,
            congruent_incorrect=result_in.congruent_incorrect,
            incongruent_correct=result_in.incongruent_correct,
            incongruent_incorrect=result_in.incongruent_incorrect,
            avg_reaction_time=result_in.avg_reaction_time,
            accuracy=accuracy,
            interference_score=interference_score,
            errors=result_in.errors,
            completion_time=result_in.completion_time
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    def save_nback_result(
        self,
        db: Session,
        result_in: NBackResultCreate
    ) -> NBackResult:
        """Guarda resultado de prueba N-Back"""
        
        # Calcular accuracy
        total_targets = result_in.hits + result_in.misses
        total_nontargets = result_in.false_alarms + result_in.correct_rejections
        
        if total_targets > 0:
            hit_rate = result_in.hits / total_targets
        else:
            hit_rate = 0
        
        if total_nontargets > 0:
            false_alarm_rate = result_in.false_alarms / total_nontargets
        else:
            false_alarm_rate = 0
        
        accuracy = (hit_rate + (1 - false_alarm_rate)) / 2 * 100
        
        result = NBackResult(
            user_id=result_in.user_id,
            session_id=result_in.session_id,
            n_level=result_in.n_level,
            total_trials=result_in.total_trials,
            hits=result_in.hits,
            misses=result_in.misses,
            false_alarms=result_in.false_alarms,
            correct_rejections=result_in.correct_rejections,
            accuracy=accuracy,
            avg_reaction_time=result_in.avg_reaction_time,
            completion_time=result_in.completion_time
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    def save_digitspan_result(
        self,
        db: Session,
        result_in: DigitSpanResultCreate
    ) -> DigitSpanResult:
        """Guarda resultado de prueba Digit Span"""
        
        result = DigitSpanResult(
            user_id=result_in.user_id,
            session_id=result_in.session_id,
            test_type=result_in.test_type,
            max_span=result_in.max_span,
            total_errors=result_in.total_errors,
            total_time=result_in.total_time,
            levels_completed=result_in.levels_completed
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    def save_trailmaking_result(
        self,
        db: Session,
        result_in: TrailMakingResultCreate
    ) -> TrailMakingResult:
        """Guarda resultado de prueba Trail Making"""
        
        result = TrailMakingResult(
            user_id=result_in.user_id,
            session_id=result_in.session_id,
            version=result_in.version,
            completion_time=result_in.completion_time,
            errors=result_in.errors,
            completed=result_in.completed,
            sequence_traced=result_in.sequence_traced
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    def save_crt_result(
        self,
        db: Session,
        result_in: CRTResultCreate
    ) -> CRTResult:
        """Guarda resultado de CRT"""
        
        # Respuestas correctas CRT
        CORRECT_ANSWERS = {
            "question_1": "5",  # Bat y pelota: $0.05
            "question_2": "5",  # 5 máquinas hacen 5 widgets en 5 min
            "question_3": "47"  # Nenúfares cubren mitad en 47 días
        }
        
        total_correct = 0
        total_time = 0
        
        if result_in.question_1_correct:
            total_correct += 1
        if result_in.question_1_time:
            total_time += result_in.question_1_time
            
        if result_in.question_2_correct:
            total_correct += 1
        if result_in.question_2_time:
            total_time += result_in.question_2_time
            
        if result_in.question_3_correct:
            total_correct += 1
        if result_in.question_3_time:
            total_time += result_in.question_3_time
        
        result = CRTResult(
            user_id=result_in.user_id,
            session_id=result_in.session_id,
            question_1_answer=result_in.question_1_answer,
            question_1_correct=result_in.question_1_correct,
            question_1_time=result_in.question_1_time,
            question_2_answer=result_in.question_2_answer,
            question_2_correct=result_in.question_2_correct,
            question_2_time=result_in.question_2_time,
            question_3_answer=result_in.question_3_answer,
            question_3_correct=result_in.question_3_correct,
            question_3_time=result_in.question_3_time,
            total_correct=total_correct,
            total_time=total_time
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result


redtic_service = REDTICService()
cognitive_tests_service = CognitiveTestsService()
