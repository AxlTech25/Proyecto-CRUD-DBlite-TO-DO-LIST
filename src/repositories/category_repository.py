from sqlalchemy.orm import Session
from src.models.category import Category
from src.repositories.base_repository import BaseRepository

class CategoryRepository(BaseRepository[Category]):
    """
    Repositorio para el modelo Category.
    Proporciona métodos específicos para interactuar con la tabla de categorías.
    """
    def __init__(self, session: Session):
        super().__init__(session, Category)
