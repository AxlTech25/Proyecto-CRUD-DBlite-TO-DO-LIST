from tests.test_base import BaseTest
from models import Task, TaskState, TaskPriority, TaskFrequency
from datetime import datetime, timedelta

class TestTaskService(BaseTest):
    """
    Pruebas unitarias para la clase TaskService.
    """
    def setUp(self):
        """
        Configura la base de datos en memoria y crea un usuario de prueba
        para las pruebas de tareas.
        """
        super().setUp()
        self.user = self.user_service.create_user({
            "nombre": "Task User",
            "correo": "taskuser@example.com",
            "contrasena": "securepassword" # Contraseña corregida a >= 6 caracteres
        })
        self.category = self.category_service.create_category({
            "nombre": "Test Category for Task"
        })

    def test_create_task_success(self):
        """
        Verifica que se puede crear una tarea con éxito.
        """
        task_data = {
            "titulo": "New Task",
            "descripcion": "Task description.",
            "id_usuario": self.user.id_usuario
        }
        task = self.task_service.create_task(task_data)
        self.assertIsInstance(task, Task)
        self.assertEqual(task.titulo, "New Task")
        self.assertEqual(task.id_usuario, self.user.id_usuario)
        self.assertEqual(task.estado, TaskState.PENDIENTE) # Default value
        self.assertEqual(task.prioridad, TaskPriority.MEDIA) # Default value

    def test_create_task_with_all_fields_success(self):
        """
        Verifica la creación de una tarea con todos los campos especificados.
        """
        future_date = datetime.now() + timedelta(days=1)
        task_data = {
            "titulo": "Full Task",
            "descripcion": "Detailed description.",
            "fecha_inicio": datetime.now(),
            "fecha_vencimiento": future_date,
            "estado": TaskState.EN_PROGRESO,
            "prioridad": TaskPriority.ALTA,
            "recurrente": True,
            "frecuencia": TaskFrequency.DIARIA,
            "id_usuario": self.user.id_usuario
        }
        task = self.task_service.create_task(task_data)
        self.assertIsInstance(task, Task)
        self.assertEqual(task.titulo, "Full Task")
        self.assertEqual(task.estado, TaskState.EN_PROGRESO)
        self.assertEqual(task.prioridad, TaskPriority.ALTA)
        self.assertTrue(task.recurrente)
        self.assertEqual(task.frecuencia, TaskFrequency.DIARIA)
        self.assertEqual(task.id_usuario, self.user.id_usuario)

    def test_create_task_missing_title(self):
        """
        Verifica que la creación de tarea falla si falta el título.
        """
        with self.assertRaises(ValueError) as cm:
            self.task_service.create_task({"id_usuario": self.user.id_usuario})
        self.assertIn("El título de la tarea es obligatorio y debe ser una cadena no vacía.", str(cm.exception))

    def test_create_task_invalid_user_id(self):
        """
        Verifica que la creación de tarea falla con un ID de usuario inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.task_service.create_task({"titulo": "Task", "id_usuario": 999})
        self.assertIn("El usuario con ID 999 no existe.", str(cm.exception))

    def test_create_task_invalid_state(self):
        """
        Verifica que la creación de tarea falla con un estado inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.task_service.create_task({"titulo": "Task", "id_usuario": self.user.id_usuario, "estado": "INVALID"})
        self.assertIn("Estado de tarea inválido. Valores permitidos: ['Pendiente', 'En progreso', 'Completada']", str(cm.exception))

    def test_create_task_invalid_priority(self):
        """
        Verifica que la creación de tarea falla con una prioridad inválida.
        """
        with self.assertRaises(ValueError) as cm:
            self.task_service.create_task({"titulo": "Task", "id_usuario": self.user.id_usuario, "prioridad": "CRITICAL"})
        self.assertIn("Prioridad de tarea inválida. Valores permitidos: ['Alta', 'Media', 'Baja']", str(cm.exception))

    def test_create_task_invalid_dates(self):
        """
        Verifica que la creación de tarea falla si la fecha de vencimiento es anterior a la fecha de inicio.
        """
        with self.assertRaises(ValueError) as cm:
            self.task_service.create_task({
                "titulo": "Task",
                "id_usuario": self.user.id_usuario,
                "fecha_inicio": datetime.now(),
                "fecha_vencimiento": datetime.now() - timedelta(days=1)
            })
        self.assertIn("La fecha de vencimiento no puede ser anterior a la fecha de inicio.", str(cm.exception))
    
    def test_create_task_frequency_without_recurrence(self):
        """
        Verifica que la creación de tarea falla si se especifica frecuencia sin recurrencia.
        """
        with self.assertRaises(ValueError) as cm:
            self.task_service.create_task({
                "titulo": "Task",
                "id_usuario": self.user.id_usuario,
                "recurrente": False,
                "frecuencia": TaskFrequency.DIARIA # Pasa un valor de frecuencia válido
            })
        self.assertIn("La frecuencia solo puede especificarse si la tarea es recurrente.", str(cm.exception))


    def test_get_task_by_id_success(self):
        """
        Verifica que se puede obtener una tarea por su ID.
        """
        task = self.task_service.create_task({"titulo": "Fetch Task", "id_usuario": self.user.id_usuario})
        fetched_task = self.task_service.get_task_by_id(task.id_tarea)
        self.assertIsNotNone(fetched_task)
        self.assertEqual(fetched_task.id_tarea, task.id_tarea)

    def test_get_task_by_id_not_found(self):
        """
        Verifica que se devuelve None si la tarea no se encuentra.
        """
        fetched_task = self.task_service.get_task_by_id(999)
        self.assertIsNone(fetched_task)

    def test_get_all_tasks_success(self):
        """
        Verifica que se pueden obtener todas las tareas.
        """
        self.task_service.create_task({"titulo": "Task 1", "id_usuario": self.user.id_usuario})
        self.task_service.create_task({"titulo": "Task 2", "id_usuario": self.user.id_usuario})
        tasks = self.task_service.get_all_tasks()
        self.assertEqual(len(tasks), 2)

    def test_update_task_success(self):
        """
        Verifica que se puede actualizar una tarea con éxito.
        """
        task = self.task_service.create_task({"titulo": "Update Task", "id_usuario": self.user.id_usuario})
        updated_task = self.task_service.update_task(task.id_tarea, {"titulo": "Updated Task Title", "estado": TaskState.COMPLETADA})
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task.titulo, "Updated Task Title")
        self.assertEqual(updated_task.estado, TaskState.COMPLETADA)

    def test_update_task_not_found(self):
        """
        Verifica que la actualización de tarea devuelve None si no se encuentra.
        """
        updated_task = self.task_service.update_task(999, {"titulo": "Non Existent"})
        self.assertIsNone(updated_task)

    def test_update_task_invalid_data(self):
        """
        Verifica que la actualización de tarea falla con datos inválidos.
        """
        task = self.task_service.create_task({"titulo": "Valid Task", "id_usuario": self.user.id_usuario})
        with self.assertRaises(ValueError) as cm:
            self.task_service.update_task(task.id_tarea, {"estado": "INVALID_STATE"})
        self.assertIn("Estado de tarea inválido.", str(cm.exception))

    def test_delete_task_success(self):
        """
        Verifica que se puede eliminar una tarea con éxito.
        """
        task = self.task_service.create_task({"titulo": "Delete Task", "id_usuario": self.user.id_usuario})
        deleted = self.task_service.delete_task(task.id_tarea)
        self.assertTrue(deleted)
        self.assertIsNone(self.task_service.get_task_by_id(task.id_tarea))

    def test_delete_task_not_found(self):
        """
        Verifica que la eliminación de tarea devuelve False si no se encuentra.
        """
        deleted = self.task_service.delete_task(999)
        self.assertFalse(deleted)

    def test_add_category_to_task_success(self):
        """
        Verifica que se puede asociar una categoría a una tarea.
        """
        task = self.task_service.create_task({"titulo": "Task for Category", "id_usuario": self.user.id_usuario})
        updated_task = self.task_service.add_category_to_task(task.id_tarea, self.category.id_categoria)
        self.assertIsNotNone(updated_task)
        self.assertEqual(len(updated_task.categorias), 1)
        self.assertEqual(updated_task.categorias[0].categoria.nombre, self.category.nombre)

    def test_add_category_to_task_invalid_category(self):
        """
        Verifica que asociar una categoría falla si la categoría no existe.
        """
        task = self.task_service.create_task({"titulo": "Task", "id_usuario": self.user.id_usuario})
        with self.assertRaises(ValueError) as cm:
            self.task_service.add_category_to_task(task.id_tarea, 999)
        self.assertIn("La categoría con ID 999 no existe.", str(cm.exception))

    def test_remove_category_from_task_success(self):
        """
        Verifica que se puede desasociar una categoría de una tarea.
        """
        task = self.task_service.create_task({"titulo": "Task for Removal", "id_usuario": self.user.id_usuario})
        self.task_service.add_category_to_task(task.id_tarea, self.category.id_categoria)
        
        updated_task = self.task_service.remove_category_from_task(task.id_tarea, self.category.id_categoria)
        self.assertIsNotNone(updated_task)
        self.assertEqual(len(updated_task.categorias), 0)

    def test_remove_category_from_task_not_associated(self):
        """
        Verifica que desasociar una categoría no afecta si no estaba asociada.
        """
        task = self.task_service.create_task({"titulo": "Task", "id_usuario": self.user.id_usuario})
        # Try to remove a category that was never added
        updated_task = self.task_service.remove_category_from_task(task.id_tarea, self.category.id_categoria)
        self.assertIsNotNone(updated_task)
        self.assertEqual(len(updated_task.categorias), 0) # Should still be 0

    def test_get_tasks_by_user_success(self):
        """
        Verifica que se pueden obtener tareas por un usuario específico.
        """
        user2 = self.user_service.create_user({"nombre": "User2", "correo": "user2@example.com", "contrasena": "password2"}) # Contraseña corregida
        self.task_service.create_task({"titulo": "Task A", "id_usuario": self.user.id_usuario})
        self.task_service.create_task({"titulo": "Task B", "id_usuario": self.user.id_usuario})
        self.task_service.create_task({"titulo": "Task C", "id_usuario": user2.id_usuario})

        user_tasks = self.task_service.get_tasks_by_user(self.user.id_usuario)
        self.assertEqual(len(user_tasks), 2)
        for task in user_tasks:
            self.assertEqual(task.id_usuario, self.user.id_usuario)
        
        user2_tasks = self.task_service.get_tasks_by_user(user2.id_usuario)
        self.assertEqual(len(user2_tasks), 1)
        self.assertEqual(user2_tasks[0].id_usuario, user2.id_usuario)
