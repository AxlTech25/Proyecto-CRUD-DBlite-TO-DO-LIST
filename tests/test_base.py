import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
from src.services import UserService, TaskService, CategoryService, NotificationService

class BaseTest(unittest.TestCase):
    """
    Clase base para pruebas unitarias.
    Configura una base de datos en memoria para cada prueba y gestiona las sesiones.
    """
    def setUp(self):
        """
        Configura la base de datos en memoria y las sesiones para cada prueba.
        """
        self.engine = create_engine('sqlite:///:memory:') # Base de datos en memoria
        Base.metadata.create_all(self.engine) # Crea las tablas
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Inicializa los servicios con la sesión de prueba
        self.user_service = UserService(self.session)
        self.task_service = TaskService(self.session)
        self.category_service = CategoryService(self.session)
        self.notification_service = NotificationService(self.session)

    def tearDown(self):
        """
        Cierra la sesión y elimina todas las tablas después de cada prueba.
        """
        self.session.close()
        Base.metadata.drop_all(self.engine) # Elimina las tablas
