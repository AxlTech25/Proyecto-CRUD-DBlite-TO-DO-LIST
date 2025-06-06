import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, TaskState, TaskPriority, TaskFrequency
from services import UserService, TaskService, CategoryService, NotificationService
from datetime import datetime, timedelta

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
    print("Creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

def main():
    """
    Función principal para demostrar las operaciones CRUD.
    """
    init_db()
    db = SessionLocal()

    try:
        user_service = UserService(db)
        task_service = TaskService(db)
        category_service = CategoryService(db)
        notification_service = NotificationService(db)

        print("\n--- Demostración de CRUD ---")

        # --- USUARIO ---
        print("\n=== Operaciones de Usuario ===")
        print("Creando usuario...")
        user_data = {
            "nombre": "Juan Pérez",
            "correo": "juan.perez@example.com",
            "contrasena": "password123"
        }
        try:
            user = user_service.create_user(user_data)
            print(f"Usuario creado: {user}")
        except ValueError as e:
            print(f"Error al crear usuario: {e}")
            user = None

        if user:
            print("\nLeyendo todos los usuarios...")
            users = user_service.get_all_users()
            for u in users:
                print(f"  - {u}")

            print(f"\nLeyendo usuario con ID {user.id_usuario}...")
            fetched_user = user_service.get_user_by_id(user.id_usuario)
            print(f"Usuario leído: {fetched_user}")

            print(f"\nActualizando nombre del usuario {user.id_usuario}...")
            updated_user = user_service.update_user(user.id_usuario, {"nombre": "Juan Carlos Pérez"})
            print(f"Usuario actualizado: {updated_user}")
            
            print(f"\nIntentando actualizar usuario con datos inválidos...")
            try:
                user_service.update_user(user.id_usuario, {"correo": "correo-invalido"})
            except ValueError as e:
                print(f"Error esperado: {e}")

        # --- CATEGORIA ---
        print("\n=== Operaciones de Categoría ===")
        print("Creando categorías...")
        try:
            category1 = category_service.create_category({"nombre": "Trabajo"})
            print(f"Categoría creada: {category1}")
            category2 = category_service.create_category({"nombre": "Personal"})
            print(f"Categoría creada: {category2}")
        except ValueError as e:
            print(f"Error al crear categoría: {e}")
            category1 = None
            category2 = None
        
        if category1 and category2:
            print("\nLeyendo todas las categorías...")
            categories = category_service.get_all_categories()
            for c in categories:
                print(f"  - {c}")

            print(f"\nActualizando nombre de la categoría {category1.id_categoria}...")
            updated_category = category_service.update_category(category1.id_categoria, {"nombre": "Desarrollo"})
            print(f"Categoría actualizada: {updated_category}")

        # --- TAREA ---
        if user:
            print("\n=== Operaciones de Tarea ===")
            print("Creando tarea...")
            task_data = {
                "titulo": "Completar informe mensual",
                "descripcion": "Redactar el informe de ventas de mayo.",
                "fecha_vencimiento": datetime.now() + timedelta(days=7),
                "estado": TaskState.EN_PROGRESO,
                "prioridad": TaskPriority.ALTA,
                "recurrente": False,
                "id_usuario": user.id_usuario
            }
            try:
                task = task_service.create_task(task_data)
                print(f"Tarea creada: {task}")
            except ValueError as e:
                print(f"Error al crear tarea: {e}")
                task = None
            
            if task:
                print("\nLeyendo todas las tareas...")
                tasks = task_service.get_all_tasks()
                for t in tasks:
                    print(f"  - {t}")
                
                print(f"\nLeyendo tarea con ID {task.id_tarea}...")
                fetched_task = task_service.get_task_by_id(task.id_tarea)
                print(f"Tarea leída: {fetched_task}")

                print(f"\nActualizando estado y descripción de la tarea {task.id_tarea}...")
                updated_task = task_service.update_task(task.id_tarea, {
                    "estado": TaskState.COMPLETADA,
                    "descripcion": "Informe mensual completado y enviado."
                })
                print(f"Tarea actualizada: {updated_task}")

                print(f"\nIntentando actualizar tarea con estado inválido...")
                try:
                    task_service.update_task(task.id_tarea, {"estado": "INVALIDO"})
                except ValueError as e:
                    print(f"Error esperado: {e}")

                # --- RELACIÓN TAREA-CATEGORIA ---
                if category1 and category2:
                    print(f"\nAsociando tarea {task.id_tarea} con categoría {category1.id_categoria}...")
                    task_with_category = task_service.add_category_to_task(task.id_tarea, category1.id_categoria)
                    print(f"Tarea con categoría: {task_with_category.titulo}, Categorías: {[tc.categoria.nombre for tc in task_with_category.categorias]}")

                    print(f"\nAsociando tarea {task.id_tarea} con categoría {category2.id_categoria}...")
                    task_with_category = task_service.add_category_to_task(task.id_tarea, category2.id_categoria)
                    print(f"Tarea con categoría: {task_with_category.titulo}, Categorías: {[tc.categoria.nombre for tc in task_with_category.categorias]}")
                    
                    print(f"\nDesasociando tarea {task.id_tarea} de categoría {category1.id_categoria}...")
                    task_without_category = task_service.remove_category_from_task(task.id_tarea, category1.id_categoria)
                    print(f"Tarea sin categoría: {task_without_category.titulo}, Categorías: {[tc.categoria.nombre for tc in task_without_category.categorias]}")

                # --- NOTIFICACION ---
                print("\n=== Operaciones de Notificación ===")
                print("Creando notificación...")
                notification_data = {
                    "id_tarea": task.id_tarea,
                    "fecha_envio": datetime.now() + timedelta(minutes=5)
                }
                try:
                    notification = notification_service.create_notification(notification_data)
                    print(f"Notificación creada: {notification}")
                except ValueError as e:
                    print(f"Error al crear notificación: {e}")
                    notification = None
                
                if notification:
                    print("\nLeyendo todas las notificaciones...")
                    notifications = notification_service.get_all_notifications()
                    for n in notifications:
                        print(f"  - {n}")

                    print(f"\nLeyendo notificación con ID {notification.id_notificacion}...")
                    fetched_notification = notification_service.get_notification_by_id(notification.id_notificacion)
                    print(f"Notificación leída: {fetched_notification}")

                    print(f"\nActualizando fecha de envío de la notificación {notification.id_notificacion}...")
                    updated_notification = notification_service.update_notification(notification.id_notificacion, {
                        "fecha_envio": datetime.now() + timedelta(minutes=15)
                    })
                    print(f"Notificación actualizada: {updated_notification}")

                    print(f"\nEliminando notificación {notification.id_notificacion}...")
                    deleted_notification = notification_service.delete_notification(notification.id_notificacion)
                    print(f"Notificación eliminada: {deleted_notification}")
                else:
                    print("No se pudo crear la notificación para la demostración.")

                print(f"\nEliminando tarea {task.id_tarea} (esto también eliminará las notificaciones asociadas)...")
                deleted_task = task_service.delete_task(task.id_tarea)
                print(f"Tarea eliminada: {deleted_task}")
            else:
                print("No se pudo crear la tarea para la demostración.")

            print(f"\nEliminando usuario {user.id_usuario} (esto también eliminará sus tareas y notificaciones)...")
            deleted_user = user_service.delete_user(user.id_usuario)
            print(f"Usuario eliminado: {deleted_user}")
        else:
            print("No se pudo crear el usuario para la demostración.")
        
        if category1:
            print(f"\nEliminando categoría {category1.id_categoria}...")
            deleted_category = category_service.delete_category(category1.id_categoria)
            print(f"Categoría eliminada: {deleted_category}")
        if category2:
            print(f"\nEliminando categoría {category2.id_categoria}...")
            deleted_category = category_service.delete_category(category2.id_categoria)
            print(f"Categoría eliminada: {deleted_category}")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        db.close()
        print("\nDemostración de CRUD finalizada.")

if __name__ == "__main__":
    main()
