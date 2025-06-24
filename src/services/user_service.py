from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from models.user import User
from typing import List, Dict, Any
import re

class UserService:
    """
    Servicio para gestionar la lógica de negocio relacionada con los usuarios.
    """
    def __init__(self, session: Session):
        self.repository = UserRepository(session)

    def _validate_user_data(self, data: Dict[str, Any], is_new: bool = True):
        """
        Valida los datos de un usuario.
        :param data: Diccionario con los datos del usuario.
        :param is_new: True si es una creación, False si es una actualización.
        :raises ValueError: Si los datos no son válidos.
        """
        if is_new:
            if not all(k in data for k in ['nombre', 'correo', 'contrasena']):
                raise ValueError("Nombre, correo y contraseña son campos obligatorios.")
        
        if 'nombre' in data and (not isinstance(data['nombre'], str) or not data['nombre'].strip()):
            raise ValueError("El nombre es obligatorio y debe ser una cadena no vacía.")
        
        if 'correo' in data:
            if not isinstance(data['correo'], str) or not re.match(r"[^@]+@[^@]+\.[^@]+", data['correo']):
                raise ValueError("El formato del correo electrónico no es válido.")
            # Basic check for existing email, more robust check would be in repository/DB constraint
            if is_new and self.repository.session.query(User).filter_by(correo=data['correo']).first():
                raise ValueError(f"Ya existe un usuario con el correo: {data['correo']}")
        
        # Validar la longitud de la contraseña
        if 'contrasena' in data:
            if not isinstance(data['contrasena'], str) or len(data['contrasena']) < 6:
                raise ValueError("La contraseña es obligatoria y debe tener al menos 6 caracteres.")

    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Crea un nuevo usuario después de validar los datos.
        :param user_data: Diccionario con los datos del usuario.
        :return: El usuario creado.
        """
        self._validate_user_data(user_data, is_new=True)
        return self.repository.add(user_data)

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Obtiene un usuario por su ID.
        :param user_id: ID del usuario.
        :return: El usuario o None.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("El ID de usuario debe ser un entero positivo.")
        return self.repository.get_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """
        Obtiene todos los usuarios.
        :return: Una lista de usuarios.
        """
        return self.repository.get_all()

    def update_user(self, user_id: int, update_data: Dict[str, Any]) -> User | None:
        """
        Actualiza un usuario existente después de validar los datos.
        :param user_id: ID del usuario a actualizar.
        :param update_data: Diccionario con los datos a actualizar.
        :return: El usuario actualizado o None.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("El ID de usuario debe ser un entero positivo.")
        self._validate_user_data(update_data, is_new=False)
        return self.repository.update(user_id, update_data)

    def delete_user(self, user_id: int) -> bool:
        """
        Elimina un usuario por su ID.
        :param user_id: ID del usuario a eliminar.
        :return: True si se eliminó con éxito, False en caso contrario.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("El ID de usuario debe ser un entero positivo.")
        return self.repository.delete(user_id)
