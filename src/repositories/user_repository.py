from sqlalchemy.orm import Session
from src.models.user import User
from src.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    Repositorio para el modelo User.
    Proporciona métodos específicos para interactuar con la tabla de usuarios.
    """
    def __init__(self, session: Session):
        super().__init__(session, User)
