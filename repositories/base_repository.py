from sqlalchemy.orm import Session
from typing import TypeVar, Generic, List, Dict, Any

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Clase base genérica para repositorios que proporciona operaciones CRUD comunes.
    """
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def add(self, entity_data: Dict[str, Any]) -> T:
        """
        Agrega una nueva entidad a la base de datos.
        :param entity_data: Diccionario con los datos de la entidad.
        :return: La entidad creada.
        """
        entity = self.model(**entity_data)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: int) -> T | None:
        """
        Obtiene una entidad por su ID.
        :param entity_id: ID de la entidad.
        :return: La entidad o None si no se encuentra.
        """
        return self.session.query(self.model).get(entity_id)

    def get_all(self) -> List[T]:
        """
        Obtiene todas las entidades de un tipo específico.
        :return: Una lista de entidades.
        """
        return self.session.query(self.model).all()

    def update(self, entity_id: int, update_data: Dict[str, Any]) -> T | None:
        """
        Actualiza una entidad existente por su ID.
        :param entity_id: ID de la entidad a actualizar.
        :param update_data: Diccionario con los datos a actualizar.
        :return: La entidad actualizada o None si no se encuentra.
        """
        entity = self.get_by_id(entity_id)
        if entity:
            for key, value in update_data.items():
                setattr(entity, key, value)
            self.session.commit()
            self.session.refresh(entity)
        return entity

    def delete(self, entity_id: int) -> bool:
        """
        Elimina una entidad por su ID.
        :param entity_id: ID de la entidad a eliminar.
        :return: True si se eliminó con éxito, False en caso contrario.
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False
