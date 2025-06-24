from sqlalchemy.orm import Session
from models.notification import Notification
from repositories.base_repository import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    """
    Repositorio para el modelo Notification.
    Proporciona métodos específicos para interactuar con la tabla de notificaciones.
    """
    def __init__(self, session: Session):
        super().__init__(session, Notification)
