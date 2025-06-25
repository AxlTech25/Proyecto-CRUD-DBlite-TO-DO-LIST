from sqlalchemy.orm import Session
from src.repositories.notification_repository import NotificationRepository
from src.models.notification import Notification
from src.models.task import Task
from typing import List, Dict, Any
from datetime import datetime

class NotificationService:
    """
    Servicio para gestionar la lógica de negocio relacionada con las notificaciones.
    """
    def __init__(self, session: Session):
        self.repository = NotificationRepository(session)
        self.session = session

    def _validate_notification_data(self, data: Dict[str, Any], is_new: bool = True):
        """
        Valida los datos de una notificación.
        :param data: Diccionario con los datos de la notificación.
        :param is_new: True si es una creación, False si es una actualización.
        :raises ValueError: Si los datos no son válidos.
        """
        if is_new:
            if 'id_tarea' not in data:
                raise ValueError("El ID de tarea es obligatorio para crear una notificación.")
            if not isinstance(data['id_tarea'], int) or data['id_tarea'] <= 0:
                raise ValueError("El ID de tarea debe ser un entero positivo.")
            # Check if task exists
            if not self.session.query(Task).get(data['id_tarea']):
                raise ValueError(f"La tarea con ID {data['id_tarea']} no existe.")

        if 'fecha_envio' in data and not isinstance(data['fecha_envio'], datetime):
            raise ValueError("La fecha de envío debe ser un objeto datetime.")

    def create_notification(self, notification_data: Dict[str, Any]) -> Notification:
        """
        Crea una nueva notificación después de validar los datos.
        :param notification_data: Diccionario con los datos de la notificación.
        :return: La notificación creada.
        """
        self._validate_notification_data(notification_data, is_new=True)
        return self.repository.add(notification_data)

    def get_notification_by_id(self, notification_id: int) -> Notification | None:
        """
        Obtiene una notificación por su ID.
        :param notification_id: ID de la notificación.
        :return: La notificación o None.
        """
        if not isinstance(notification_id, int) or notification_id <= 0:
            raise ValueError("El ID de notificación debe ser un entero positivo.")
        return self.repository.get_by_id(notification_id)

    def get_all_notifications(self) -> List[Notification]:
        """
        Obtiene todas las notificaciones.
        :return: Una lista de notificaciones.
        """
        return self.repository.get_all()

    def update_notification(self, notification_id: int, update_data: Dict[str, Any]) -> Notification | None:
        """
        Actualiza una notificación existente después de validar los datos.
        :param notification_id: ID de la notificación a actualizar.
        :param update_data: Diccionario con los datos a actualizar.
        :return: La notificación actualizada o None.
        """
        if not isinstance(notification_id, int) or notification_id <= 0:
            raise ValueError("El ID de notificación debe ser un entero positivo.")
        self._validate_notification_data(update_data, is_new=False)
        return self.repository.update(notification_id, update_data)

    def delete_notification(self, notification_id: int) -> bool:
        """
        Elimina una notificación por su ID.
        :param notification_id: ID de la notificación a eliminar.
        :return: True si se eliminó con éxito, False en caso contrario.
        """
        if not isinstance(notification_id, int) or notification_id <= 0:
            raise ValueError("El ID de notificación debe ser un entero positivo.")
        return self.repository.delete(notification_id)
