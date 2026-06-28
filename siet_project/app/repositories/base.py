"""
Repositorio base para operaciones CRUD
"""

from typing import Generic, Type, TypeVar, Optional, List, Any
from sqlalchemy.orm import Session
from app.db.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repositorio base con operaciones CRUD genéricas.
    
    Args:
        model: Clase del modelo SQLAlchemy
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Obtiene un registro por ID.
        
        Args:
            db: Sesión de base de datos
            id: ID del registro
            
        Returns:
            El registro o None si no existe
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtiene todos los registros con paginación.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de registros
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: Any) -> ModelType:
        """
        Crea un nuevo registro.
        
        Args:
            db: Sesión de base de datos
            obj_in: Objeto con los datos a crear
            
        Returns:
            El registro creado
        """
        obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: Any
    ) -> ModelType:
        """
        Actualiza un registro existente.
        
        Args:
            db: Sesión de base de datos
            db_obj: Registro a actualizar
            obj_in: Objeto con los datos actualizados
            
        Returns:
            El registro actualizado
        """
        obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
        
        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Elimina un registro por ID.
        
        Args:
            db: Sesión de base de datos
            id: ID del registro a eliminar
            
        Returns:
            El registro eliminado o None si no existe
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def get_by_field(
        self,
        db: Session,
        field: str,
        value: Any
    ) -> Optional[ModelType]:
        """
        Obtiene un registro por un campo específico.
        
        Args:
            db: Sesión de base de datos
            field: Nombre del campo
            value: Valor del campo
            
        Returns:
            El registro o None si no existe
        """
        return db.query(self.model).filter(
            getattr(self.model, field) == value
        ).first()
    
    def get_multi_by_field(
        self,
        db: Session,
        field: str,
        value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Obtiene múltiples registros por un campo específico.
        
        Args:
            db: Sesión de base de datos
            field: Nombre del campo
            value: Valor del campo
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de registros
        """
        return db.query(self.model).filter(
            getattr(self.model, field) == value
        ).offset(skip).limit(limit).all()
