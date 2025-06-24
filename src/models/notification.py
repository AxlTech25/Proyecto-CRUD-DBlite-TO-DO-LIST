from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Notification(Base):
    """
    Modelo de Notificación.
    Representa una notificación asociada a una tarea.
    """
    __tablename__ = 'notifications'

    id_notificacion = Column(Integer, primary_key=True, index=True)
    id_tarea = Column(Integer, ForeignKey('tasks.id_tarea'), nullable=False)
    fecha_envio = Column(DateTime, default=datetime.now, nullable=False)

    # Relación muchos-a-uno con Tarea
    tarea = relationship("Task", back_populates="notificaciones")

    def __repr__(self):
        return (f"<Notification(id_notificacion={self.id_notificacion}, "
                f"id_tarea={self.id_tarea}, fecha_envio='{self.fecha_envio}')>")
