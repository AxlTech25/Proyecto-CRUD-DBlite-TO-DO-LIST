import os
import sys
from datetime import datetime, timedelta
import functools # ¡Nueva libreria utilizada para poder modificar el codigo sin necesidad de reescribir la logica!

# Importaciones para PyQt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QMessageBox,
    QHeaderView, QAbstractItemView, QDateTimeEdit, QComboBox, QCheckBox, QTextEdit,
    QWidget, QHBoxLayout, QPushButton
)
from PyQt5 import uic
from PyQt5.QtCore import QDateTime, Qt # Importar Qt para flags de QMessageBox

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Importar modelos y servicios de tu proyecto
from src.models import Base, User, Task, Category, Notification, TaskState, TaskPriority, TaskFrequency
from src.services import UserService, TaskService, CategoryService, NotificationService

# --- Configuración de la base de datos ---
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True) # ensure_directories_exist

DATABASE_URL = f"sqlite:///{DATA_DIR}/database.db"
engine = create_engine(DATABASE_URL)

# Asegurarse de que las tablas estén creadas
Base.metadata.create_all(bind=engine)

# Configurar SessionLocal para el manejo de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

class TaskManagerApp(QMainWindow):
    """
    Clase principal de la aplicación GUI para el Gestor de Tareas.
    Carga la interfaz de usuario desde un archivo .ui y conecta la lógica de negocio.
    """
    def __init__(self):
        super().__init__()
        # Cargar la interfaz de usuario desde el archivo .ui
        ui_file_path = os.path.join(os.path.dirname(__file__), 'task_manager_ui.ui')
        if not os.path.exists(ui_file_path):
            QMessageBox.critical(self, "Error de Carga",
                                 f"No se encontró el archivo UI: {ui_file_path}\n"
                                 "Asegúrate de que 'task_manager_ui.ui' esté en el mismo directorio que 'app_gui.py'.")
            sys.exit(1)
        uic.loadUi(ui_file_path, self)

        # Inicializar servicios de la base de datos
        self.db = db_session()
        self.user_service = UserService(self.db)
        self.category_service = CategoryService(self.db)
        self.task_service = TaskService(self.db)
        self.notification_service = NotificationService(self.db)

        # Variables para almacenar el ID de la entidad seleccionada (para edición)
        self.current_user_id = None
        self.current_category_id = None
        self.current_task_id = None
        self.current_notification_id = None

        # Conectar señales y slots
        self._connect_signals_slots()
        # Configurar tablas y cargar datos iniciales
        self._setup_tables()
        self._load_initial_data()

    def _connect_signals_slots(self):
        """
        Conecta los eventos de los widgets con los métodos de la aplicación.
        """
        # --- Pestaña de Usuarios ---
        self.saveUserButton.clicked.connect(self._save_user)
        self.clearUserButton.clicked.connect(self._clear_user_form)
        self.usersTable.cellClicked.connect(self._load_user_into_form)

        # --- Pestaña de Categorías ---
        self.saveCategoryButton.clicked.connect(self._save_category)
        self.clearCategoryButton.clicked.connect(self._clear_category_form)
        self.categoriesTable.cellClicked.connect(self._load_category_into_form)

        # --- Pestaña de Tareas ---
        self.saveTaskButton.clicked.connect(self._save_task)
        self.clearTaskButton.clicked.connect(self._clear_task_form)
        self.tasksTable.cellClicked.connect(self._load_task_into_form)
        self.taskRecurringInput.stateChanged.connect(self._toggle_task_frequency)
        self.addCategoryToTaskButton.clicked.connect(self._add_category_to_selected_task)
        self.removeCategoryFromTaskButton.clicked.connect(self._remove_category_from_selected_task)

        # --- Pestaña de Notificaciones ---
        self.saveNotificationButton.clicked.connect(self._save_notification)
        self.clearNotificationButton.clicked.connect(self._clear_notification_form)
        self.notificationsTable.cellClicked.connect(self._load_notification_into_form)

        # Manejar el cambio de pestaña para recargar datos
        self.tabWidget.currentChanged.connect(self._on_tab_changed)

    def _setup_tables(self):
        """
        Configura los encabezados y el comportamiento de las tablas.
        """
        # Tabla de Usuarios
        self.usersTable.setColumnCount(4)
        self.usersTable.setHorizontalHeaderLabels(["ID", "Nombre", "Correo", "Acciones"])
        self.usersTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # PyQt5
        self.usersTable.setSelectionBehavior(QAbstractItemView.SelectRows) # PyQt5

        # Tabla de Categorías
        self.categoriesTable.setColumnCount(3)
        self.categoriesTable.setHorizontalHeaderLabels(["ID", "Nombre", "Acciones"])
        self.categoriesTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # PyQt5
        self.categoriesTable.setSelectionBehavior(QAbstractItemView.SelectRows) # PyQt5

        # Tabla de Tareas
        self.tasksTable.setColumnCount(7)
        self.tasksTable.setHorizontalHeaderLabels(["ID", "Título", "Estado", "Prioridad", "Usuario (ID)", "Categorías", "Acciones"])
        self.tasksTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # PyQt5
        self.tasksTable.setSelectionBehavior(QAbstractItemView.SelectRows) # PyQt5

        # Tabla de Notificaciones
        self.notificationsTable.setColumnCount(4)
        self.notificationsTable.setHorizontalHeaderLabels(["ID", "Tarea (ID)", "Fecha de Envío", "Acciones"])
        self.notificationsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # PyQt5
        self.notificationsTable.setSelectionBehavior(QAbstractItemView.SelectRows) # PyQt5
        
        # Llenar ComboBoxes de enums
        self.taskStateInput.addItems([e.value for e in TaskState])
        self.taskPriorityInput.addItems([p.value for p in TaskPriority])
        # Asegurarse de que el QComboBox para frecuencia pueda tener una opción vacía
        self.taskFrequencyInput.addItem("") # Opción vacía al principio
        self.taskFrequencyInput.addItems([f.value for f in TaskFrequency])

        # Establecer la fecha/hora actual por defecto para los QDateTimeEdit
        self.taskStartDateInput.setDateTime(QDateTime.currentDateTime())
        self.notificationSendDateInput.setDateTime(QDateTime.currentDateTime())

    def _load_initial_data(self):
        """
        Carga los datos iniciales en las tablas y comboboxes.
        """
        self._load_users()
        self._load_categories()
        self._load_tasks()
        self._load_notifications()
        self._populate_user_combobox()
        self._populate_category_combobox()
        self._populate_task_combobox()
        self._toggle_task_frequency() # Ajustar estado inicial de frecuencia

    def _on_tab_changed(self, index):
        """
        Maneja el cambio de pestaña para recargar datos específicos de la pestaña activa.
        """
        tab_name = self.tabWidget.tabText(index)
        if tab_name == "Usuarios":
            self._load_users()
        elif tab_name == "Categorías":
            self._load_categories()
        elif tab_name == "Tareas":
            self._load_tasks()
            self._populate_user_combobox() # Recargar usuarios por si hay nuevos
            self._populate_category_combobox() # Recargar categorías por si hay nuevas
            self._clear_task_form()
        elif tab_name == "Notificaciones":
            self._load_notifications()
            self._populate_task_combobox() # Recargar tareas por si hay nuevas
            self._clear_notification_form()


    # --- Funciones Auxiliares para Mensajes ---
    def _show_info_message(self, title, message):
        """Muestra un mensaje de información."""
        QMessageBox.information(self, title, message)

    def _show_warning_message(self, title, message):
        """Muestra un mensaje de advertencia."""
        QMessageBox.warning(self, title, message)

    def _show_error_message(self, title, message):
        """Muestra un mensaje de error."""
        QMessageBox.critical(self, title, message)

    # --- Funciones de Serialización/Deserialización para la UI ---
    def _to_qt_datetime(self, dt_obj: datetime | None) -> QDateTime:
        """Convierte un objeto datetime de Python a QDateTime de PyQt."""
        if dt_obj:
            return QDateTime(dt_obj.year, dt_obj.month, dt_obj.day,
                             dt_obj.hour, dt_obj.minute, dt_obj.second)
        return QDateTime() # Devuelve un QDateTime nulo si no hay objeto datetime

    def _from_qt_datetime(self, qt_dt_obj: QDateTime) -> datetime | None:
        """Convierte un objeto QDateTime de PyQt a datetime de Python."""
        if qt_dt_obj.isValid():
            return qt_dt_obj.toPyDateTime()
        return None

    def _get_enum_value(self, enum_class, string_value):
        """Obtiene el miembro del enum a partir de su valor string."""
        for member in enum_class:
            if member.value == string_value:
                return member
        return None # O lanzar un error si el valor no es válido

    # --- CRUD Usuarios ---
    def _load_users(self):
        """Carga los usuarios de la base de datos y los muestra en la tabla."""
        self.usersTable.setRowCount(0) # Limpiar tabla
        users = self.user_service.get_all_users()
        for row_idx, user in enumerate(users):
            print(f"DEBUG: Processing user from DB: ID={user.id_usuario}, Name={user.nombre}, Type ID={type(user.id_usuario)}") # NEW DEBUG PRINT
            
            # Ensure id_usuario is int and positive before setting
            user_id_for_display = None
            try:
                user_id_for_display = int(user.id_usuario)
                if user_id_for_display <= 0:
                    raise ValueError("ID de usuario no es positivo.")
            except (ValueError, TypeError) as e:
                print(f"DEBUG: Skipping user due to invalid ID during load: {user.id_usuario} - {e}")
                continue # Skip this row if ID is invalid

            self.usersTable.insertRow(row_idx) # Insert row only if ID is valid
            self.usersTable.setItem(row_idx, 0, QTableWidgetItem(str(user_id_for_display)))
            self.usersTable.setItem(row_idx, 1, QTableWidgetItem(user.nombre))
            self.usersTable.setItem(row_idx, 2, QTableWidgetItem(user.correo))

            # Añadir botones de acciones usando functools.partial
            actions_cell = self._create_actions_widget(
                edit_func=functools.partial(self._load_user_into_form, row_idx, 0),
                delete_func=functools.partial(self._delete_user, user_id_for_display)
            )
            self.usersTable.setCellWidget(row_idx, 3, actions_cell)

    def _save_user(self):
        """Guarda o actualiza un usuario."""
        name = self.userNameInput.text().strip()
        email = self.userEmailInput.text().strip()
        password = self.userPasswordInput.text()

        user_data = {
            "nombre": name,
            "correo": email,
            "contrasena": password
        }

        try:
            if self.current_user_id: # Actualizar usuario existente
                # Solo incluir la contraseña si ha sido modificada (no vacía)
                if not password:
                    user_data.pop("contrasena") # No actualizar contraseña si se deja vacía
                
                updated_user = self.user_service.update_user(self.current_user_id, user_data)
                if updated_user:
                    self._show_info_message("Éxito", "Usuario actualizado con éxito!")
                else:
                    self._show_error_message("Error", "Usuario no encontrado para actualizar.")
            else: # Crear nuevo usuario
                new_user = self.user_service.create_user(user_data)
                self._show_info_message("Éxito", "Usuario creado con éxito!")

            self._clear_user_form()
            self._load_users()
            self._populate_user_combobox() # Recargar combobox de usuarios

        except ValueError as e:
            self._show_warning_message("Error de Validación", str(e))
        except Exception as e:
            self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
        finally:
            self.db.commit() # Asegurarse de que los cambios se guarden o se reviertan

    def _load_user_into_form(self, row, column):
        """Carga los datos de un usuario seleccionado en el formulario para edición."""
        self.current_user_id = None # Reiniciar por si hay errores

        item = self.usersTable.item(row, 0)
        if item is None or not item.text():
            self._show_error_message("Error de Lectura", "No se pudo obtener el ID del usuario de la tabla. Celda vacía.")
            return

        try:
            user_id_from_table = int(item.text())
            if user_id_from_table <= 0:
                raise ValueError("El ID de usuario de la tabla no es positivo.")
            self.current_user_id = user_id_from_table
        except ValueError as e:
            self._show_error_message("Error de Lectura", f"ID de usuario inválido en la tabla: {e}. Valor: '{item.text()}'")
            return

        user = self.user_service.get_user_by_id(self.current_user_id)
        if user:
            self.userNameInput.setText(user.nombre)
            self.userEmailInput.setText(user.correo)
            # No cargar la contraseña por seguridad; el usuario debe reintroducirla para cambiarla.
            self.userPasswordInput.clear()
        else:
            # Esto puede pasar si el usuario fue eliminado por otra operación justo antes de hacer click
            self._show_warning_message("Usuario No Encontrado", f"El usuario con ID {self.current_user_id} no se encontró en la base de datos.")
            self.current_user_id = None # Resetear el ID actual ya que no existe
            self._clear_user_form() # Limpiar formulario si no se encuentra
            self._load_users() # Recargar la tabla para reflejar el estado actual

    def _delete_user(self, user_id):
        """Elimina un usuario previa confirmación."""
        print(f"DEBUG: Attempting to delete user_id: {user_id}, type: {type(user_id)}") # DEBUG PRINT
        # Validación defensiva del ID antes de llamar al servicio
        if not isinstance(user_id, int) or user_id <= 0:
            print("DEBUG: Validation failed for user_id in _delete_user.") # DEBUG PRINT
            self._show_warning_message("Error de Eliminación", "ID de usuario inválido para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación',
                                     f"¿Estás seguro de que quieres eliminar el usuario ID: {user_id}?\n"
                                     "Esto también eliminará todas sus tareas y notificaciones asociadas.",
                                     QMessageBox.Yes | QMessageBox.No, # PyQt5
                                     QMessageBox.No) # PyQt5
        if reply == QMessageBox.Yes: # PyQt5
            try:
                deleted = self.user_service.delete_user(user_id)
                if deleted:
                    self._show_info_message("Éxito", "Usuario eliminado con éxito.")
                else:
                    self._show_warning_message("Advertencia", "Usuario no encontrado.")
                self._load_users()
                self._populate_user_combobox() # Recargar combobox de usuarios
                self._load_tasks() # Recargar tareas por si se eliminaron cascada
                self._load_notifications() # Recargar notificaciones por si se eliminaron cascada
                self._clear_user_form() # Limpiar formulario después de eliminar
            except ValueError as e:
                self._show_warning_message("Error de Validación", str(e))
            except Exception as e:
                self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
            finally:
                self.db.commit()

    def _clear_user_form(self):
        """Limpia el formulario de usuario."""
        self.current_user_id = None
        self.userNameInput.clear()
        self.userEmailInput.clear()
        self.userPasswordInput.clear()

    def _populate_user_combobox(self):
        """Rellena el QComboBox de usuarios en la pestaña de Tareas."""
        self.taskUserInput.clear()
        self.taskUserInput.addItem("--- Seleccionar Usuario ---", userData=None)
        users = self.user_service.get_all_users()
        for user in users:
            self.taskUserInput.addItem(f"{user.nombre} (ID: {user.id_usuario})", userData=user.id_usuario)

    # --- CRUD Categorías ---
    def _load_categories(self):
        """Carga las categorías de la base de datos y las muestra en la tabla."""
        self.categoriesTable.setRowCount(0)
        categories = self.category_service.get_all_categories()
        for row_idx, category in enumerate(categories):
            self.categoriesTable.insertRow(row_idx)
            self.categoriesTable.setItem(row_idx, 0, QTableWidgetItem(str(category.id_categoria)))
            self.categoriesTable.setItem(row_idx, 1, QTableWidgetItem(category.nombre))

            actions_cell = self._create_actions_widget(
                edit_func=functools.partial(self._load_category_into_form, row_idx, 0),
                delete_func=functools.partial(self._delete_category, category.id_categoria)
            )
            self.categoriesTable.setCellWidget(row_idx, 2, actions_cell)

    def _save_category(self):
        """Guarda o actualiza una categoría."""
        name = self.categoryNameInput.text().strip()
        category_data = {"nombre": name}

        try:
            if self.current_category_id:
                updated_category = self.category_service.update_category(self.current_category_id, category_data)
                if updated_category:
                    self._show_info_message("Éxito", "Categoría actualizada con éxito!")
                else:
                    self._show_error_message("Error", "Categoría no encontrada para actualizar.")
            else:
                new_category = self.category_service.create_category(category_data)
                self._show_info_message("Éxito", "Categoría creada con éxito!")
            
            self._clear_category_form()
            self._load_categories()
            self._populate_category_combobox() # Recargar combobox de categorías
        except ValueError as e:
            self._show_warning_message("Error de Validación", str(e))
        except Exception as e:
            self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
        finally:
            self.db.commit()

    def _load_category_into_form(self, row, column):
        """Carga los datos de una categoría seleccionada en el formulario."""
        self.current_category_id = None

        item = self.categoriesTable.item(row, 0)
        if item is None or not item.text():
            self._show_error_message("Error de Lectura", "No se pudo obtener el ID de la categoría de la tabla. Celda vacía.")
            return

        try:
            category_id_from_table = int(item.text())
            if category_id_from_table <= 0:
                raise ValueError("El ID de categoría de la tabla no es positivo.")
            self.current_category_id = category_id_from_table
        except ValueError as e:
            self._show_error_message("Error de Lectura", f"ID de categoría inválido en la tabla: {e}. Valor: '{item.text()}'")
            return

        category = self.category_service.get_category_by_id(self.current_category_id)
        if category:
            self.categoryNameInput.setText(category.nombre)
        else:
            self._show_warning_message("Categoría No Encontrada", f"La categoría con ID {self.current_category_id} no se encontró en la base de datos.")
            self.current_category_id = None
            self._clear_category_form()
            self._load_categories()

    def _delete_category(self, category_id):
        """Elimina una categoría previa confirmación."""
        if not isinstance(category_id, int) or category_id <= 0:
            self._show_warning_message("Error de Eliminación", "ID de categoría inválido para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación',
                                     f"¿Estás seguro de que quieres eliminar la categoría ID: {category_id}?",
                                     QMessageBox.Yes | QMessageBox.No, # PyQt5
                                     QMessageBox.No) # PyQt5
        if reply == QMessageBox.Yes: # PyQt5
            try:
                deleted = self.category_service.delete_category(category_id)
                if deleted:
                    self._show_info_message("Éxito", "Categoría eliminada con éxito.")
                else:
                    self._show_warning_message("Advertencia", "Categoría no encontrada.")
                self._load_categories()
                self._populate_category_combobox() # Recargar combobox de categorías
                self._load_tasks() # Recargar tareas por si afectó categorías asociadas
                self._clear_category_form() # Limpiar formulario después de eliminar
            except ValueError as e:
                self._show_warning_message("Error de Validación", str(e))
            except Exception as e:
                self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
            finally:
                self.db.commit()

    def _clear_category_form(self):
        """Limpia el formulario de categoría."""
        self.current_category_id = None
        self.categoryNameInput.clear()

    def _populate_category_combobox(self):
        """Rellena el QComboBox de categorías en la pestaña de Tareas."""
        self.taskCategorySelect.clear()
        self.taskCategorySelect.addItem("--- Seleccionar Categoría ---", userData=None)
        categories = self.category_service.get_all_categories()
        for category in categories:
            self.taskCategorySelect.addItem(f"{category.nombre} (ID: {category.id_categoria})", userData=category.id_categoria)

    # --- CRUD Tareas ---
    def _toggle_task_frequency(self):
        """Habilita/deshabilita el QComboBox de frecuencia según si la tarea es recurrente."""
        self.taskFrequencyInput.setEnabled(self.taskRecurringInput.isChecked())
        if not self.taskRecurringInput.isChecked():
            self.taskFrequencyInput.setCurrentIndex(0) # Seleccionar opción vacía

    def _load_tasks(self):
        """Carga las tareas de la base de datos y las muestra en la tabla."""
        self.tasksTable.setRowCount(0)
        tasks = self.task_service.get_all_tasks()
        for row_idx, task in enumerate(tasks):
            self.tasksTable.insertRow(row_idx)
            self.tasksTable.setItem(row_idx, 0, QTableWidgetItem(str(task.id_tarea)))
            self.tasksTable.setItem(row_idx, 1, QTableWidgetItem(task.titulo))
            self.tasksTable.setItem(row_idx, 2, QTableWidgetItem(task.estado.value))
            self.tasksTable.setItem(row_idx, 3, QTableWidgetItem(task.prioridad.value))
            self.tasksTable.setItem(row_idx, 4, QTableWidgetItem(str(task.id_usuario)))

            # Mostrar categorías asociadas
            categories_str = ", ".join([tc.categoria.nombre for tc in task.categorias if tc.categoria])
            self.tasksTable.setItem(row_idx, 5, QTableWidgetItem(categories_str if categories_str else "N/A"))

            actions_cell = self._create_actions_widget(
                edit_func=functools.partial(self._load_task_into_form, row_idx, 0),
                delete_func=functools.partial(self._delete_task, task.id_tarea)
            )
            self.tasksTable.setCellWidget(row_idx, 6, actions_cell)

    def _save_task(self):
        """Guarda o actualiza una tarea."""
        title = self.taskTitleInput.text().strip()
        description = self.taskDescriptionInput.toPlainText().strip()
        start_date = self._from_qt_datetime(self.taskStartDateInput.dateTime())
        due_date = self._from_qt_datetime(self.taskDueDateInput.dateTime())
        state = self._get_enum_value(TaskState, self.taskStateInput.currentText())
        priority = self._get_enum_value(TaskPriority, self.taskPriorityInput.currentText())
        recurring = self.taskRecurringInput.isChecked()
        frequency_str = self.taskFrequencyInput.currentText()
        frequency = self._get_enum_value(TaskFrequency, frequency_str) if recurring and frequency_str else None
        
        user_id_data = self.taskUserInput.currentData()
        if user_id_data is None:
            self._show_warning_message("Error de Validación", "Por favor, selecciona un usuario para la tarea.")
            return

        task_data = {
            "titulo": title,
            "descripcion": description if description else None,
            "fecha_inicio": start_date,
            "fecha_vencimiento": due_date,
            "estado": state,
            "prioridad": priority,
            "recurrente": recurring,
            "frecuencia": frequency,
            "id_usuario": user_id_data
        }

        try:
            if self.current_task_id:
                updated_task = self.task_service.update_task(self.current_task_id, task_data)
                if updated_task:
                    self._show_info_message("Éxito", "Tarea actualizada con éxito!")
                else:
                    self._show_error_message("Error", "Tarea no encontrada para actualizar.")
            else:
                new_task = self.task_service.create_task(task_data)
                self._show_info_message("Éxito", "Tarea creada con éxito!")
            
            self._clear_task_form()
            self._load_tasks()
            self._populate_task_combobox() # Recargar combobox de tareas

        except ValueError as e:
            self._show_warning_message("Error de Validación", str(e))
        except Exception as e:
            self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
        finally:
            self.db.commit()

    def _load_task_into_form(self, row, column):
        """Carga los datos de una tarea seleccionada en el formulario."""
        self.current_task_id = None

        item = self.tasksTable.item(row, 0)
        if item is None or not item.text():
            self._show_error_message("Error de Lectura", "No se pudo obtener el ID de la tarea de la tabla. Celda vacía.")
            return

        try:
            task_id_from_table = int(item.text())
            if task_id_from_table <= 0:
                raise ValueError("El ID de tarea de la tabla no es positivo.")
            self.current_task_id = task_id_from_table
        except ValueError as e:
            self._show_error_message("Error de Lectura", f"ID de tarea inválido en la tabla: {e}. Valor: '{item.text()}'")
            return

        task = self.task_service.get_task_by_id(self.current_task_id)
        if task:
            self.taskTitleInput.setText(task.titulo)
            self.taskDescriptionInput.setText(task.descripcion if task.descripcion else "")
            self.taskStartDateInput.setDateTime(self._to_qt_datetime(task.fecha_inicio))
            self.taskDueDateInput.setDateTime(self._to_qt_datetime(task.fecha_vencimiento))
            self.taskStateInput.setCurrentText(task.estado.value)
            self.taskPriorityInput.setCurrentText(task.prioridad.value)
            self.taskRecurringInput.setChecked(task.recurrente)
            self.taskFrequencyInput.setCurrentText(task.frecuencia.value if task.frecuencia else "")
            self._toggle_task_frequency() # Ajustar enabled/disabled
            
            # Seleccionar usuario en el combobox
            user_index = self.taskUserInput.findData(task.id_usuario)
            if user_index != -1:
                self.taskUserInput.setCurrentIndex(user_index)
            else:
                self.taskUserInput.setCurrentIndex(0) # Seleccionar "Seleccionar Usuario"

        else:
            self._show_warning_message("Tarea No Encontrada", f"La tarea con ID {self.current_task_id} no se encontró en la base de datos.")
            self.current_task_id = None
            self._clear_task_form()
            self._load_tasks()

    def _delete_task(self, task_id):
        """Elimina una tarea previa confirmación."""
        if not isinstance(task_id, int) or task_id <= 0:
            self._show_warning_message("Error de Eliminación", "ID de tarea inválido para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación',
                                     f"¿Estás seguro de que quieres eliminar la tarea ID: {task_id}?\n"
                                     "Esto también eliminará las notificaciones asociadas.",
                                     QMessageBox.Yes | QMessageBox.No, # PyQt5
                                     QMessageBox.No) # PyQt5
        if reply == QMessageBox.Yes: # PyQt5
            try:
                deleted = self.task_service.delete_task(task_id)
                if deleted:
                    self._show_info_message("Éxito", "Tarea eliminada con éxito.")
                else:
                    self._show_warning_message("Advertencia", "Tarea no encontrada.")
                self._load_tasks()
                self._populate_task_combobox() # Recargar combobox de tareas
                self._load_notifications() # Recargar notificaciones
                self._clear_task_form() # Limpiar formulario después de eliminar
            except ValueError as e:
                self._show_warning_message("Error de Validación", str(e))
            except Exception as e:
                self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
            finally:
                self.db.commit()

    def _clear_task_form(self):
        """Limpia el formulario de tarea."""
        self.current_task_id = None
        self.taskTitleInput.clear()
        self.taskDescriptionInput.clear()
        self.taskStartDateInput.setDateTime(QDateTime.currentDateTime())
        self.taskDueDateInput.clear() # Limpiar fecha de vencimiento
        self.taskStateInput.setCurrentIndex(0) # Pendiente
        self.taskPriorityInput.setCurrentIndex(1) # Media
        self.taskRecurringInput.setChecked(False)
        self.taskFrequencyInput.setCurrentIndex(0) # Vacío
        self._toggle_task_frequency()
        self.taskUserInput.setCurrentIndex(0) # --- Seleccionar Usuario ---

    def _add_category_to_selected_task(self):
        """Asocia la categoría seleccionada a la tarea actualmente cargada en el formulario."""
        if self.current_task_id is None:
            self._show_warning_message("Advertencia", "Por favor, selecciona una tarea para asociar una categoría.")
            return

        category_id_data = self.taskCategorySelect.currentData()
        if category_id_data is None:
            self._show_warning_message("Advertencia", "Por favor, selecciona una categoría para asociar.")
            return
        
        try:
            updated_task = self.task_service.add_category_to_task(self.current_task_id, category_id_data)
            if updated_task:
                self._show_info_message("Éxito", f"Categoría asociada a la tarea ID: {self.current_task_id}.")
                self._load_tasks() # Recargar tabla de tareas para reflejar la categoría
            else:
                self._show_error_message("Error", "No se pudo asociar la categoría. La tarea o categoría no existe, o ya está asociada.")
        except ValueError as e:
            self._show_warning_message("Error de Validación", str(e))
        except Exception as e:
            self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
        finally:
                self.db.commit()

    def _remove_category_from_selected_task(self):
        """Desasocia la categoría seleccionada de la tarea actualmente cargada en el formulario."""
        if self.current_task_id is None:
            self._show_warning_message("Advertencia", "Por favor, selecciona una tarea para desasociar una categoría.")
            return

        category_id_data = self.taskCategorySelect.currentData()
        if category_id_data is None:
            self._show_warning_message("Advertencia", "Por favor, selecciona una categoría para desasociar.")
            return
        
        try:
            updated_task = self.task_service.remove_category_from_task(self.current_task_id, category_id_data)
            if updated_task:
                self._show_info_message("Éxito", f"Categoría desasociada de la tarea ID: {self.current_task_id}.")
                self._load_tasks() # Recargar tabla de tareas
            else:
                self._show_error_message("Error", "No se pudo desasociar la categoría. La tarea o asociación no existe.")
        except ValueError as e:
            self._show_warning_message("Error de Validación", str(e))
        except Exception as e:
            self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
        finally:
            self.db.commit()

    def _populate_task_combobox(self):
        """Rellena el QComboBox de tareas en la pestaña de Notificaciones."""
        self.notificationTaskInput.clear()
        self.notificationTaskInput.addItem("--- Seleccionar Tarea ---", userData=None)
        tasks = self.task_service.get_all_tasks()
        for task in tasks:
            self.notificationTaskInput.addItem(f"{task.titulo} (ID: {task.id_tarea})", userData=task.id_tarea)

    # --- CRUD Notificaciones ---
    def _load_notifications(self):
        """Carga las notificaciones de la base de datos y las muestra en la tabla."""
        self.notificationsTable.setRowCount(0)
        notifications = self.notification_service.get_all_notifications()
        for row_idx, notification in enumerate(notifications):
            self.notificationsTable.insertRow(row_idx)
            self.notificationsTable.setItem(row_idx, 0, QTableWidgetItem(str(notification.id_notificacion)))
            self.notificationsTable.setItem(row_idx, 1, QTableWidgetItem(str(notification.id_tarea)))
            self.notificationsTable.setItem(row_idx, 2, QTableWidgetItem(notification.fecha_envio.strftime("%Y-%m-%d %H:%M:%S")))

            actions_cell = self._create_actions_widget(
                edit_func=functools.partial(self._load_notification_into_form, row_idx, 0),
                delete_func=functools.partial(self._delete_notification, notification.id_notificacion)
            )
            self.notificationsTable.setCellWidget(row_idx, 3, actions_cell)

    def _save_notification(self):
        """Guarda o actualiza una notificación."""
        task_id_data = self.notificationTaskInput.currentData()
        if task_id_data is None:
            self._show_warning_message("Error de Validación", "Por favor, selecciona una tarea para la notificación.")
            return

        send_date = self._from_qt_datetime(self.notificationSendDateInput.dateTime())

        notification_data = {
            "id_tarea": task_id_data,
            "fecha_envio": send_date
        }

        try:
            if self.current_notification_id:
                updated_notification = self.notification_service.update_notification(self.current_notification_id, notification_data)
                if updated_notification:
                    self._show_info_message("Éxito", "Notificación actualizada con éxito!")
                else:
                    self._show_error_message("Error", "Notificación no encontrada para actualizar.")
            else:
                new_notification = self.notification_service.create_notification(notification_data)
                self._show_info_message("Éxito", "Notificación creada con éxito!")
            
            self._clear_notification_form()
            self._load_notifications()
        except ValueError as e:
            self._show_warning_message("Error de Validación", str(e))
        except Exception as e:
            self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
        finally:
            self.db.commit()

    def _load_notification_into_form(self, row, column):
        """Carga los datos de una notificación seleccionada en el formulario."""
        self.current_notification_id = None

        item = self.notificationsTable.item(row, 0)
        if item is None or not item.text():
            self._show_error_message("Error de Lectura", "No se pudo obtener el ID de la notificación de la tabla. Celda vacía.")
            return

        try:
            notification_id_from_table = int(item.text())
            if notification_id_from_table <= 0:
                raise ValueError("El ID de notificación de la tabla no es positivo.")
            self.current_notification_id = notification_id_from_table
        except ValueError as e:
            self._show_error_message("Error de Lectura", f"ID de notificación inválido en la tabla: {e}. Valor: '{item.text()}'")
            return

        notification = self.notification_service.get_notification_by_id(self.current_notification_id)
        if notification:
            # Seleccionar tarea en el combobox
            task_index = self.notificationTaskInput.findData(notification.id_tarea)
            if task_index != -1:
                self.notificationTaskInput.setCurrentIndex(task_index)
            else:
                self.notificationTaskInput.setCurrentIndex(0) # Seleccionar "Seleccionar Tarea"

            self.notificationSendDateInput.setDateTime(self._to_qt_datetime(notification.fecha_envio))
        else:
            self._show_warning_message("Notificación No Encontrada", f"La notificación con ID {self.current_notification_id} no se encontró en la base de datos.")
            self.current_notification_id = None
            self._clear_notification_form()
            self._load_notifications()

    def _delete_notification(self, notification_id):
        """Elimina una notificación previa confirmación."""
        if not isinstance(notification_id, int) or notification_id <= 0:
            self._show_warning_message("Error de Eliminación", "ID de notificación inválido para eliminar.")
            return

        reply = QMessageBox.question(self, 'Confirmar Eliminación',
                                     f"¿Estás seguro de que quieres eliminar la notificación ID: {notification_id}?",
                                     QMessageBox.Yes | QMessageBox.No, # PyQt5
                                     QMessageBox.No) # PyQt5
        if reply == QMessageBox.Yes: # PyQt5
            try:
                deleted = self.notification_service.delete_notification(notification_id)
                if deleted:
                    self._show_info_message("Éxito", "Notificación eliminada con éxito.")
                else:
                    self._show_warning_message("Advertencia", "Notificación no encontrada.")
                    self._load_notifications()
                    self._clear_notification_form() # Limpiar formulario después de eliminar
            except ValueError as e:
                self._show_warning_message("Error de Validación", str(e))
            except Exception as e:
                self._show_error_message("Error del Sistema", f"Ocurrió un error inesperado: {e}")
            finally:
                self.db.commit()

    def _clear_notification_form(self):
        """Limpia el formulario de notificación."""
        self.current_notification_id = None
        self.notificationTaskInput.setCurrentIndex(0) # --- Seleccionar Tarea ---
        self.notificationSendDateInput.setDateTime(QDateTime.currentDateTime())

    def _create_actions_widget(self, edit_func, delete_func):
        """
        Crea un widget con botones de 'Editar' y 'Eliminar' para las celdas de acción de la tabla.
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0) # Eliminar márgenes para que los botones estén más juntos
        layout.setSpacing(5) # Espacio entre botones

        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(edit_func)
        edit_button.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 5px; padding: 5px 10px;") # Estilo básico

        delete_button = QPushButton("Eliminar")
        delete_button.clicked.connect(delete_func)
        delete_button.setStyleSheet("background-color: #ef4444; color: white; border-radius: 5px; padding: 5px 10px;") # Estilo básico
        
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addStretch() # Empujar los botones hacia la izquierda

        return widget

    def closeEvent(self, event):
        """
        Se ejecuta cuando la ventana se cierra, asegurando que la sesión de la base de datos se cierre.
        """
        if self.db:
            self.db.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManagerApp()
    window.show()
    sys.exit(app.exec_()) # En PyQt5, es app.exec_()
