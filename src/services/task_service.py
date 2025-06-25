from sqlalchemy.orm import Session
from src.repositories.task_repository import TaskRepository
from src.models.task import Task, TaskState, TaskPriority, TaskFrequency
from src.models.user import User
from src.models.category import Category
from typing import List, Dict, Any
from datetime import datetime

class TaskService:
    """
    Servicio para gestionar la lógica de negocio relacionada con las tareas.
    """
    def __init__(self, session: Session):
        self.repository = TaskRepository(session)
        self.session = session

    def _validate_task_data(self, data: Dict[str, Any], is_new: bool = True):
        """
        Valida los datos de una tarea.
        :param data: Diccionario con los datos de la tarea.
        :param is_new: True si es una creación, False si es una actualización.
        :raises ValueError: Si los datos no son válidos.
        """
        if is_new:
            if 'titulo' not in data or not isinstance(data['titulo'], str) or not data['titulo'].strip():
                raise ValueError("El título de la tarea es obligatorio y debe ser una cadena no vacía.")
            if 'id_usuario' not in data:
                raise ValueError("El ID de usuario es obligatorio para crear una tarea.")
            if not isinstance(data['id_usuario'], int) or data['id_usuario'] <= 0:
                raise ValueError("El ID de usuario debe ser un entero positivo.")
            # Check if user exists
            if not self.session.query(User).get(data['id_usuario']):
                raise ValueError(f"El usuario con ID {data['id_usuario']} no existe.")

        if 'titulo' in data and (not isinstance(data['titulo'], str) or not data['titulo'].strip()):
            raise ValueError("El título de la tarea debe ser una cadena no vacía.")

        if 'descripcion' in data and not isinstance(data['descripcion'], str):
            raise ValueError("La descripción debe ser una cadena de texto.")

        if 'fecha_inicio' in data and not isinstance(data['fecha_inicio'], datetime):
            raise ValueError("La fecha de inicio debe ser un objeto datetime.")

        if 'fecha_vencimiento' in data:
            if not isinstance(data['fecha_vencimiento'], datetime):
                raise ValueError("La fecha de vencimiento debe ser un objeto datetime.")
            if 'fecha_inicio' in data and data['fecha_vencimiento'] < data['fecha_inicio']:
                raise ValueError("La fecha de vencimiento no puede ser anterior a la fecha de inicio.")

        if 'estado' in data:
            if not isinstance(data['estado'], TaskState):
                try:
                    data['estado'] = TaskState[data['estado'].upper()]
                except KeyError:
                    raise ValueError(f"Estado de tarea inválido. Valores permitidos: {[e.value for e in TaskState]}")

        if 'prioridad' in data:
            if not isinstance(data['prioridad'], TaskPriority):
                try:
                    data['prioridad'] = TaskPriority[data['prioridad'].upper()]
                except KeyError:
                    raise ValueError(f"Prioridad de tarea inválida. Valores permitidos: {[p.value for p in TaskPriority]}")

        if 'recurrente' in data and not isinstance(data['recurrente'], bool):
            raise ValueError("El campo 'recurrente' debe ser un booleano.")

        # Corregir la validación de frecuencia
        if 'frecuencia' in data and data['frecuencia'] is not None:
            if not data.get('recurrente', False): # Si hay frecuencia pero no es recurrente
                raise ValueError("La frecuencia solo puede especificarse si la tarea es recurrente.")
            if not isinstance(data['frecuencia'], TaskFrequency):
                try:
                    data['frecuencia'] = TaskFrequency[data['frecuencia'].upper()]
                except KeyError:
                    raise ValueError(f"Frecuencia de tarea inválida. Valores permitidos: {[f.value for f in TaskFrequency]}")
        
        # Si la tarea no es recurrente, la frecuencia debe ser None
        if 'recurrente' in data and not data['recurrente'] and 'frecuencia' in data and data['frecuencia'] is not None:
            raise ValueError("La frecuencia no debe especificarse si la tarea no es recurrente.")


    def create_task(self, task_data: Dict[str, Any]) -> Task:
        """
        Crea una nueva tarea después de validar los datos.
        :param task_data: Diccionario con los datos de la tarea.
        :return: La tarea creada.
        """
        self._validate_task_data(task_data, is_new=True)
        return self.repository.add(task_data)

    def get_task_by_id(self, task_id: int) -> Task | None:
        """
        Obtiene una tarea por su ID.
        :param task_id: ID de la tarea.
        :return: La tarea o None.
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("El ID de tarea debe ser un entero positivo.")
        return self.repository.get_by_id(task_id)

    def get_all_tasks(self) -> List[Task]:
        """
        Obtiene todas las tareas.
        :return: Una lista de tareas.
        """
        return self.repository.get_all()

    def update_task(self, task_id: int, update_data: Dict[str, Any]) -> Task | None:
        """
        Actualiza una tarea existente después de validar los datos.
        :param task_id: ID de la tarea a actualizar.
        :param update_data: Diccionario con los datos a actualizar.
        :return: La tarea actualizada o None.
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("El ID de tarea debe ser un entero positivo.")
        self._validate_task_data(update_data, is_new=False)
        return self.repository.update(task_id, update_data)

    def delete_task(self, task_id: int) -> bool:
        """
        Elimina una tarea por su ID.
        :param task_id: ID de la tarea a eliminar.
        :return: True si se eliminó con éxito, False en caso contrario.
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("El ID de tarea debe ser un entero positivo.")
        return self.repository.delete(task_id)

    def add_category_to_task(self, task_id: int, category_id: int) -> Task | None:
        """
        Asocia una categoría a una tarea.
        :param task_id: ID de la tarea.
        :param category_id: ID de la categoría.
        :return: La tarea actualizada o None.
        """
        if not self.session.query(Category).get(category_id):
            raise ValueError(f"La categoría con ID {category_id} no existe.")
        return self.repository.add_category_to_task(task_id, category_id)

    def remove_category_from_task(self, task_id: int, category_id: int) -> Task | None:
        """
        Desasocia una categoría de una tarea.
        :param task_id: ID de la tarea.
        :param category_id: ID de la categoría.
        :return: La tarea actualizada o None.
        """
        return self.repository.remove_category_from_task(task_id, category_id)

    def get_tasks_by_user(self, user_id: int) -> List[Task]:
        """
        Obtiene todas las tareas asociadas a un usuario específico.
        :param user_id: ID del usuario.
        :return: Una lista de tareas.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("El ID de usuario debe ser un entero positivo.")
        return self.repository.get_tasks_by_user(user_id)
