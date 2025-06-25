from sqlalchemy.orm import Session
from src.models.task import Task, TaskCategory
from src.models.category import Category
from src.repositories.base_repository import BaseRepository
from typing import List

class TaskRepository(BaseRepository[Task]):
    """
    Repositorio para el modelo Task.
    Proporciona métodos específicos para interactuar con la tabla de tareas,
    incluyendo la gestión de categorías.
    """
    def __init__(self, session: Session):
        super().__init__(session, Task)

    def add_category_to_task(self, task_id: int, category_id: int) -> Task | None:
        """
        Asocia una categoría a una tarea existente.
        :param task_id: ID de la tarea.
        :param category_id: ID de la categoría.
        :return: La tarea actualizada o None si no se encuentra.
        """
        task = self.get_by_id(task_id)
        category = self.session.query(Category).get(category_id)
        if task and category:
            # Check if the association already exists
            existing_association = self.session.query(TaskCategory).filter_by(
                id_tarea=task_id, id_categoria=category_id
            ).first()
            if not existing_association:
                association = TaskCategory(id_tarea=task_id, id_categoria=category_id)
                task.categorias.append(association) # Add to the relationship
                self.session.commit()
                self.session.refresh(task)
            return task
        return None

    def remove_category_from_task(self, task_id: int, category_id: int) -> Task | None:
        """
        Desasocia una categoría de una tarea existente.
        :param task_id: ID de la tarea.
        :param category_id: ID de la categoría.
        :return: La tarea actualizada o None si no se encuentra.
        """
        task = self.get_by_id(task_id)
        if task:
            association_to_delete = self.session.query(TaskCategory).filter_by(
                id_tarea=task_id, id_categoria=category_id
            ).first()
            if association_to_delete:
                self.session.delete(association_to_delete)
                self.session.commit()
                self.session.refresh(task)
            return task
        return None

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """
        Obtiene todas las tareas asociadas a un usuario específico.
        :param user_id: ID del usuario.
        :return: Una lista de tareas.
        """
        return self.session.query(self.model).filter_by(id_usuario=user_id).all()
