import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, TaskState, TaskPriority, TaskFrequency, Category, Task, Notification
from services import UserService, TaskService, CategoryService, NotificationService
from datetime import datetime, timedelta
import random

# Asegura que el directorio 'data' exista
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DATABASE_URL = f"sqlite:///{DATA_DIR}/database.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Inicializa la base de datos, creando todas las tablas si no existen.
    """
    print("Creando tablas de la base de datos si no existen...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas/verificadas exitosamente.")

def generate_simulated_data(num_users=5, num_categories=5, tasks_per_user=5, notifications_per_task=1):
    """
    Genera datos simulados y los inserta en la base de datos.
    :param num_users: Número de usuarios a crear.
    :param num_categories: Número de categorías a crear.
    :param tasks_per_user: Número promedio de tareas por usuario.
    :param notifications_per_task: Número de notificaciones por tarea.
    """
    db = SessionLocal()
    try:
        user_service = UserService(db)
        task_service = TaskService(db)
        category_service = CategoryService(db)
        notification_service = NotificationService(db)

        # --- Generar Usuarios ---
        print(f"\n--- Generando {num_users} usuarios simulados ---")
        created_users = []
        for i in range(1, num_users + 1):
            user_data = {
                "nombre": f"Usuario {i}",
                "correo": f"usuario{i}@example.com",
                "contrasena": "password123"
            }
            try:
                user = user_service.create_user(user_data)
                created_users.append(user)
                print(f"  Creado: {user.nombre} ({user.correo})")
            except ValueError as e:
                print(f"  Error al crear usuario {user_data['nombre']}: {e}")

        # --- Generar Categorías ---
        print(f"\n--- Generando {num_categories} categorías simuladas ---")
        created_categories = []
        for i in range(1, num_categories + 1):
            category_data = {
                "nombre": f"Categoría {i}"
            }
            try:
                category = category_service.create_category(category_data)
                created_categories.append(category)
                print(f"  Creada: {category.nombre}")
            except ValueError as e:
                print(f"  Error al crear categoría {category_data['nombre']}: {e}")

        if not created_users:
            print("No se pudieron crear usuarios. No se generarán tareas ni notificaciones.")
            return
        if not created_categories:
            print("No se pudieron crear categorías. Las tareas no se asociarán con categorías.")

        # --- Generar Tareas ---
        print(f"\n--- Generando tareas simuladas (aprox. {tasks_per_user} por usuario) ---")
        created_tasks = []
        for user in created_users:
            for i in range(tasks_per_user):
                titulo = f"Tarea de {user.nombre} #{i+1}"
                descripcion = f"Descripción detallada para la tarea {titulo}."
                fecha_inicio = datetime.now() - timedelta(days=random.randint(0, 30))
                fecha_vencimiento = fecha_inicio + timedelta(days=random.randint(1, 60))
                
                estado = random.choice(list(TaskState))
                prioridad = random.choice(list(TaskPriority))
                recurrente = random.choice([True, False])
                frecuencia = random.choice(list(TaskFrequency)) if recurrente else None

                task_data = {
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "fecha_inicio": fecha_inicio,
                    "fecha_vencimiento": fecha_vencimiento,
                    "estado": estado,
                    "prioridad": prioridad,
                    "recurrente": recurrente,
                    "frecuencia": frecuencia,
                    "id_usuario": user.id_usuario
                }
                try:
                    task = task_service.create_task(task_data)
                    created_tasks.append(task)
                    print(f"  Creada: '{task.titulo}' para {user.nombre}")

                    # Asociar categorías aleatorias a la tarea
                    if created_categories and random.random() < 0.7: # 70% de probabilidad de tener categorías
                        num_categories_to_add = random.randint(1, min(len(created_categories), 2))
                        selected_categories = random.sample(created_categories, num_categories_to_add)
                        for cat in selected_categories:
                            try:
                                task_service.add_category_to_task(task.id_tarea, cat.id_categoria)
                                # print(f"    Asociada categoría: {cat.nombre}")
                            except ValueError as e:
                                print(f"    Error al asociar categoría {cat.nombre} a tarea {task.titulo}: {e}")

                except ValueError as e:
                    print(f"  Error al crear tarea '{titulo}': {e}")
        
        # --- Generar Notificaciones ---
        print(f"\n--- Generando notificaciones simuladas (aprox. {notifications_per_task} por tarea) ---")
        for task in created_tasks:
            if random.random() < 0.8: # 80% de probabilidad de tener notificaciones
                for i in range(notifications_per_task):
                    fecha_envio = task.fecha_vencimiento - timedelta(hours=random.randint(1, 72)) # Antes del vencimiento
                    notification_data = {
                        "id_tarea": task.id_tarea,
                        "fecha_envio": fecha_envio
                    }
                    try:
                        notification = notification_service.create_notification(notification_data)
                        print(f"  Creada notificación para '{task.titulo}' en {notification.fecha_envio.strftime('%Y-%m-%d %H:%M')}")
                    except ValueError as e:
                        print(f"  Error al crear notificación para tarea '{task.titulo}': {e}")

        print("\n--- Generación de datos simulados completada. ---")

    except Exception as e:
        print(f"Ocurrió un error inesperado durante la generación de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    generate_simulated_data(
        num_users=10,        # Crea 10 usuarios
        num_categories=8,    # Crea 8 categorías
        tasks_per_user=7,    # Cada usuario tendrá alrededor de 7 tareas
        notifications_per_task=2 # Cada tarea tendrá alrededor de 2 notificaciones
    )
    print("\nPara verificar los datos, puedes ejecutar 'main.py' o escribir consultas SQL directamente.")
