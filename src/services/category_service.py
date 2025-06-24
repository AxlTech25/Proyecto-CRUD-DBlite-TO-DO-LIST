from sqlalchemy.orm import Session
from repositories.category_repository import CategoryRepository
from models.category import Category
from typing import List, Dict, Any

class CategoryService:
    """
    Servicio para gestionar la lógica de negocio relacionada con las categorías.
    """
    def __init__(self, session: Session):
        self.repository = CategoryRepository(session)

    def _validate_category_data(self, data: Dict[str, Any], is_new: bool = True):
        """
        Valida los datos de una categoría.
        :param data: Diccionario con los datos de la categoría.
        :param is_new: True si es una creación, False si es una actualización.
        :raises ValueError: Si los datos no son válidos.
        """
        if is_new:
            if 'nombre' not in data or not isinstance(data['nombre'], str) or not data['nombre'].strip():
                raise ValueError("El nombre de la categoría es obligatorio y debe ser una cadena no vacía.")
            # Basic check for existing name, more robust check would be in repository/DB constraint
            if self.repository.session.query(Category).filter_by(nombre=data['nombre']).first():
                raise ValueError(f"Ya existe una categoría con el nombre: {data['nombre']}")

        if 'nombre' in data and (not isinstance(data['nombre'], str) or not data['nombre'].strip()):
            raise ValueError("El nombre de la categoría debe ser una cadena no vacía.")

    def create_category(self, category_data: Dict[str, Any]) -> Category:
        """
        Crea una nueva categoría después de validar los datos.
        :param category_data: Diccionario con los datos de la categoría.
        :return: La categoría creada.
        """
        self._validate_category_data(category_data, is_new=True)
        return self.repository.add(category_data)

    def get_category_by_id(self, category_id: int) -> Category | None:
        """
        Obtiene una categoría por su ID.
        :param category_id: ID de la categoría.
        :return: La categoría o None.
        """
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError("El ID de categoría debe ser un entero positivo.")
        return self.repository.get_by_id(category_id)

    def get_all_categories(self) -> List[Category]:
        """
        Obtiene todas las categorías.
        :return: Una lista de categorías.
        """
        return self.repository.get_all()

    def update_category(self, category_id: int, update_data: Dict[str, Any]) -> Category | None:
        """
        Actualiza una categoría existente después de validar los datos.
        :param category_id: ID de la categoría a actualizar.
        :param update_data: Diccionario con los datos a actualizar.
        :return: La categoría actualizada o None.
        """
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError("El ID de categoría debe ser un entero positivo.")
        self._validate_category_data(update_data, is_new=False)
        return self.repository.update(category_id, update_data)

    def delete_category(self, category_id: int) -> bool:
        """
        Elimina una categoría por su ID.
        :param category_id: ID de la categoría a eliminar.
        :return: True si se eliminó con éxito, False en caso contrario.
        """
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError("El ID de categoría debe ser un entero positivo.")
        return self.repository.delete(category_id)
