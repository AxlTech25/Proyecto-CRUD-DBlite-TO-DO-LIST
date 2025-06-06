from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base

class User(Base):
    """
    Modelo de Usuario.
    Representa a un usuario en el sistema.
    """
    __tablename__ = 'users'

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)

    # Relación uno-a-muchos con Tarea
    tareas = relationship("Task", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id_usuario={self.id_usuario}, nombre='{self.nombre}', correo='{self.correo}')>"
