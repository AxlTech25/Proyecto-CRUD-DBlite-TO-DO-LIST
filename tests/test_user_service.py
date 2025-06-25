from tests.test_base import BaseTest
from src.models import User

class TestUserService(BaseTest):
    """
    Pruebas unitarias para la clase UserService.
    """
    def test_create_user_success(self):
        """
        Verifica que se puede crear un usuario con éxito.
        """
        user_data = {"nombre": "Test User", "correo": "test@example.com", "contrasena": "password123"}
        user = self.user_service.create_user(user_data)
        self.assertIsInstance(user, User)
        self.assertEqual(user.nombre, "Test User")
        self.assertEqual(user.correo, "test@example.com")
        self.assertIsNotNone(user.id_usuario)

    def test_create_user_missing_fields(self):
        """
        Verifica que la creación de usuario falla si faltan campos obligatorios.
        """
        with self.assertRaises(ValueError) as cm:
            self.user_service.create_user({"nombre": "Partial User"})
        self.assertIn("Nombre, correo y contraseña son campos obligatorios.", str(cm.exception))

    def test_create_user_invalid_email(self):
        """
        Verifica que la creación de usuario falla con un correo electrónico inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.user_service.create_user({"nombre": "Bad Email", "correo": "bad-email", "contrasena": "password123"})
        self.assertIn("El formato del correo electrónico no es válido.", str(cm.exception))

    def test_create_user_duplicate_email(self):
        """
        Verifica que la creación de usuario falla con un correo electrónico duplicado.
        """
        self.user_service.create_user({"nombre": "User One", "correo": "duplicate@example.com", "contrasena": "password1"})
        with self.assertRaises(ValueError) as cm:
            self.user_service.create_user({"nombre": "User Two", "correo": "duplicate@example.com", "contrasena": "password2"})
        self.assertIn("Ya existe un usuario con el correo: duplicate@example.com", str(cm.exception))

    def test_get_user_by_id_success(self):
        """
        Verifica que se puede obtener un usuario por su ID.
        """
        user = self.user_service.create_user({"nombre": "Fetch User", "correo": "fetch@example.com", "contrasena": "password123"})
        fetched_user = self.user_service.get_user_by_id(user.id_usuario)
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.id_usuario, user.id_usuario)

    def test_get_user_by_id_not_found(self):
        """
        Verifica que se devuelve None si el usuario no se encuentra.
        """
        fetched_user = self.user_service.get_user_by_id(999)
        self.assertIsNone(fetched_user)

    def test_get_user_by_id_invalid_id(self):
        """
        Verifica que la obtención de usuario falla con un ID inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.user_service.get_user_by_id(0)
        self.assertIn("El ID de usuario debe ser un entero positivo.", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            self.user_service.get_user_by_id("abc")
        self.assertIn("El ID de usuario debe ser un entero positivo.", str(cm.exception))

    def test_get_all_users_success(self):
        """
        Verifica que se pueden obtener todos los usuarios.
        """
        self.user_service.create_user({"nombre": "User 1", "correo": "user1@example.com", "contrasena": "password1"})
        self.user_service.create_user({"nombre": "User 2", "correo": "user2@example.com", "contrasena": "password2"})
        users = self.user_service.get_all_users()
        self.assertEqual(len(users), 2)

    def test_update_user_success(self):
        """
        Verifica que se puede actualizar un usuario con éxito.
        """
        user = self.user_service.create_user({"nombre": "Update User", "correo": "update@example.com", "contrasena": "password123"})
        updated_user = self.user_service.update_user(user.id_usuario, {"nombre": "Updated Name", "correo": "new_update@example.com"})
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.nombre, "Updated Name")
        self.assertEqual(updated_user.correo, "new_update@example.com")

    def test_update_user_not_found(self):
        """
        Verifica que la actualización de usuario devuelve None si no se encuentra.
        """
        updated_user = self.user_service.update_user(999, {"nombre": "Non Existent"})
        self.assertIsNone(updated_user)

    def test_update_user_invalid_data(self):
        """
        Verifica que la actualización de usuario falla con datos inválidos.
        """
        user = self.user_service.create_user({"nombre": "Valid User", "correo": "user@example.com", "contrasena": "password_valid"})
        with self.assertRaises(ValueError) as cm:
            self.user_service.update_user(user.id_usuario, {"correo": "invalid-email"})
        self.assertIn("El formato del correo electrónico no es válido.", str(cm.exception))

    def test_delete_user_success(self):
        """
        Verifica que se puede eliminar un usuario con éxito.
        """
        user = self.user_service.create_user({"nombre": "Delete User", "correo": "delete@example.com", "contrasena": "password123"})
        deleted = self.user_service.delete_user(user.id_usuario)
        self.assertTrue(deleted)
        self.assertIsNone(self.user_service.get_user_by_id(user.id_usuario))

    def test_delete_user_not_found(self):
        """
        Verifica que la eliminación de usuario devuelve False si no se encuentra.
        """
        deleted = self.user_service.delete_user(999)
        self.assertFalse(deleted)

    def test_delete_user_invalid_id(self):
        """
        Verifica que la eliminación de usuario falla con un ID inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.user_service.delete_user(-1)
        self.assertIn("El ID de usuario debe ser un entero positivo.", str(cm.exception))
