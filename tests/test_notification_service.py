from tests.test_base import BaseTest
from src.models import Notification, TaskState
from datetime import datetime, timedelta

class TestNotificationService(BaseTest):
    """
    Pruebas unitarias para la clase NotificationService.
    """
    def setUp(self):
        """
        Configura la base de datos en memoria y crea un usuario y una tarea de prueba
        para las pruebas de notificaciones.
        """
        super().setUp()
        self.user = self.user_service.create_user({
            "nombre": "Notification User",
            "correo": "notificationuser@example.com",
            "contrasena": "password"
        })
        self.task = self.task_service.create_task({
            "titulo": "Task for Notification",
            "id_usuario": self.user.id_usuario
        })

    def test_create_notification_success(self):
        """
        Verifica que se puede crear una notificación con éxito.
        """
        notification_data = {
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now() + timedelta(minutes=10)
        }
        notification = self.notification_service.create_notification(notification_data)
        self.assertIsInstance(notification, Notification)
        self.assertEqual(notification.id_tarea, self.task.id_tarea)
        self.assertIsNotNone(notification.id_notificacion)

    def test_create_notification_missing_task_id(self):
        """
        Verifica que la creación de notificación falla si falta el ID de tarea.
        """
        with self.assertRaises(ValueError) as cm:
            self.notification_service.create_notification({"fecha_envio": datetime.now()})
        self.assertIn("El ID de tarea es obligatorio para crear una notificación.", str(cm.exception))

    def test_create_notification_invalid_task_id(self):
        """
        Verifica que la creación de notificación falla con un ID de tarea inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.notification_service.create_notification({"id_tarea": 999, "fecha_envio": datetime.now()})
        self.assertIn("La tarea con ID 999 no existe.", str(cm.exception))

    def test_create_notification_invalid_date_type(self):
        """
        Verifica que la creación de notificación falla con un tipo de fecha de envío inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.notification_service.create_notification({"id_tarea": self.task.id_tarea, "fecha_envio": "not_a_date"})
        self.assertIn("La fecha de envío debe ser un objeto datetime.", str(cm.exception))

    def test_get_notification_by_id_success(self):
        """
        Verifica que se puede obtener una notificación por su ID.
        """
        notification = self.notification_service.create_notification({
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now()
        })
        fetched_notification = self.notification_service.get_notification_by_id(notification.id_notificacion)
        self.assertIsNotNone(fetched_notification)
        self.assertEqual(fetched_notification.id_notificacion, notification.id_notificacion)

    def test_get_notification_by_id_not_found(self):
        """
        Verifica que se devuelve None si la notificación no se encuentra.
        """
        fetched_notification = self.notification_service.get_notification_by_id(999)
        self.assertIsNone(fetched_notification)
    
    def test_get_notification_by_id_invalid_id(self):
        """
        Verifica que la obtención de notificación falla con un ID inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.notification_service.get_notification_by_id(0)
        self.assertIn("El ID de notificación debe ser un entero positivo.", str(cm.exception))

    def test_get_all_notifications_success(self):
        """
        Verifica que se pueden obtener todas las notificaciones.
        """
        self.notification_service.create_notification({"id_tarea": self.task.id_tarea, "fecha_envio": datetime.now()})
        self.notification_service.create_notification({"id_tarea": self.task.id_tarea, "fecha_envio": datetime.now() + timedelta(hours=1)})
        notifications = self.notification_service.get_all_notifications()
        self.assertEqual(len(notifications), 2)

    def test_update_notification_success(self):
        """
        Verifica que se puede actualizar una notificación con éxito.
        """
        notification = self.notification_service.create_notification({
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now()
        })
        new_date = datetime.now() + timedelta(days=1)
        updated_notification = self.notification_service.update_notification(notification.id_notificacion, {"fecha_envio": new_date})
        self.assertIsNotNone(updated_notification)
        self.assertEqual(updated_notification.fecha_envio.date(), new_date.date())

    def test_update_notification_not_found(self):
        """
        Verifica que la actualización de notificación devuelve None si no se encuentra.
        """
        updated_notification = self.notification_service.update_notification(999, {"fecha_envio": datetime.now()})
        self.assertIsNone(updated_notification)

    def test_update_notification_invalid_data(self):
        """
        Verifica que la actualización de notificación falla con datos inválidos.
        """
        notification = self.notification_service.create_notification({
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now()
        })
        with self.assertRaises(ValueError) as cm:
            self.notification_service.update_notification(notification.id_notificacion, {"fecha_envio": "invalid_date"})
        self.assertIn("La fecha de envío debe ser un objeto datetime.", str(cm.exception))

    def test_delete_notification_success(self):
        """
        Verifica que se puede eliminar una notificación con éxito.
        """
        notification = self.notification_service.create_notification({
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now()
        })
        deleted = self.notification_service.delete_notification(notification.id_notificacion)
        self.assertTrue(deleted)
        self.assertIsNone(self.notification_service.get_notification_by_id(notification.id_notificacion))

    def test_delete_notification_not_found(self):
        """
        Verifica que la eliminación de notificación devuelve False si no se encuentra.
        """
        deleted = self.notification_service.delete_notification(999)
        self.assertFalse(deleted)
    
    def test_delete_notification_invalid_id(self):
        """
        Verifica que la eliminación de notificación falla con un ID inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.notification_service.delete_notification(-1)
        self.assertIn("El ID de notificación debe ser un entero positivo.", str(cm.exception))

    def test_cascade_delete_task_deletes_notifications(self):
        """
        Verifica que eliminar una tarea también elimina sus notificaciones asociadas.
        """
        notification1 = self.notification_service.create_notification({
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now()
        })
        notification2 = self.notification_service.create_notification({
            "id_tarea": self.task.id_tarea,
            "fecha_envio": datetime.now() + timedelta(hours=1)
        })

        self.assertIsNotNone(self.notification_service.get_notification_by_id(notification1.id_notificacion))
        self.assertIsNotNone(self.notification_service.get_notification_by_id(notification2.id_notificacion))

        self.task_service.delete_task(self.task.id_tarea)

        self.assertIsNone(self.notification_service.get_notification_by_id(notification1.id_notificacion))
        self.assertIsNone(self.notification_service.get_notification_by_id(notification2.id_notificacion))
