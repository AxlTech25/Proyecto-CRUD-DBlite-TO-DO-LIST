import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from models.base import Base

class TaskState(enum.Enum):
    """
    Enumeración para el estado de una tarea.
    """
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    COMPLETADA = "Completada"

class TaskPriority(enum.Enum):
    """
    Enumeración para la prioridad de una tarea.
    """
    ALTA = "Alta"
    MEDIA = "Media"
    BAJA = "Baja"

class TaskFrequency(enum.Enum):
    """
    Enumeración para la frecuencia de una tarea recurrente.
    """
    DIARIA = "Diaria"
    SEMANAL = "Semanal"
    MENSUAL = "Mensual"

class TaskCategory(Base):
    """
    Tabla de asociación para la relación muchos-a-muchos entre Tarea y Categoría.
    """
    __tablename__ = 'task_categories'
    id_tarea = Column(Integer, ForeignKey('tasks.id_tarea'), primary_key=True)
    id_categoria = Column(Integer, ForeignKey('categories.id_categoria'), primary_key=True)

    tarea = relationship("Task", back_populates="categorias")
    categoria = relationship("Category", back_populates="tareas")

    def __repr__(self):
        return f"<TaskCategory(id_tarea={self.id_tarea}, id_categoria={self.id_categoria})>"

class Task(Base):
    """
    Modelo de Tarea.
    Representa una tarea en el sistema.
    """
    __tablename__ = 'tasks'

    id_tarea = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha_inicio = Column(DateTime, default=datetime.now)
    fecha_vencimiento = Column(DateTime, nullable=True)
    estado = Column(Enum(TaskState), default=TaskState.PENDIENTE, nullable=False)
    prioridad = Column(Enum(TaskPriority), default=TaskPriority.MEDIA, nullable=False)
    recurrente = Column(Boolean, default=False)
    frecuencia = Column(Enum(TaskFrequency), nullable=True)
    id_usuario = Column(Integer, ForeignKey('users.id_usuario'), nullable=False)

    # Relación muchos-a-uno con Usuario
    usuario = relationship("User", back_populates="tareas")
    # Relación uno-a-muchos con Notificación
    notificaciones = relationship("Notification", back_populates="tarea", cascade="all, delete-orphan")
    # Relación muchos-a-muchos con Category a través de TaskCategory
    categorias = relationship("TaskCategory", back_populates="tarea", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"<Task(id_tarea={self.id_tarea}, titulo='{self.titulo}', "
                f"estado='{self.estado.value}', id_usuario={self.id_usuario})>")
