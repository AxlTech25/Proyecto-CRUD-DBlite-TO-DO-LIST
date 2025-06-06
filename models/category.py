from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base
from models.task import TaskCategory  # Importar la tabla de asociación

class Category(Base):
    """
    Modelo de Categoría.
    Representa una categoría para organizar tareas.
    """
    __tablename__ = 'categories'

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

    # Relación muchos-a-muchos con Tarea a través de TaskCategory
    tareas = relationship("TaskCategory", back_populates="categoria", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id_categoria={self.id_categoria}, nombre='{self.nombre}')>"
