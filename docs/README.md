# Sistema de Gestión de Tareas (CRUD Python con SQLAlchemy y SQLite)

Este proyecto implementa un sistema básico de gestión de tareas con funcionalidades CRUD (Crear, Leer, Actualizar, Eliminar) para Usuarios, Tareas, Categorías y Notificaciones. Está diseñado siguiendo un patrón de arquitectura por capas para promover la modularidad y la mantenibilidad.

## Características

* **CRUD Completo**: Operaciones de creación, lectura, actualización y eliminación para todas las entidades.

* **Base de Datos SQLite**: Almacenamiento persistente de datos en un archivo local.

* **SQLAlchemy ORM**: Interacción con la base de datos a través de un ORM, facilitando el manejo de objetos Python como registros de la base de datos.

* **Validaciones Básicas**: Verificación de campos obligatorios, tipos de datos y formatos (ej. correo electrónico, longitud de contraseña).

* **Pruebas Unitarias Robustas**: Cobertura de pruebas para la lógica de negocio, utilizando una base de datos en memoria para asegurar el aislamiento.
* 
* **Tener una estructura organizada (ej: src/, docs/, tests/).

* **Diseño por Capas**: Organización clara del código en `models`, `repositories` y `services`.

* **Relaciones de Base de Datos**: Manejo de relaciones uno-a-muchos (Usuario-Tarea, Tarea-Notificación) y muchos-a-muchos (Tarea-Categoría).

## Estructura del Proyecto

```
proyecto/
├── docs/
│   ├── .gitignore          # Exporta los modelos
│   ├── README.md           # Instruccion de Ejecución
├── src/
├── models/
│   ├── __init__.py          # Exporta los modelos
│   ├── base.py              # Base declarativa de SQLAlchemy
│   ├── category.py          # Modelo de Categoría
│   ├── notification.py      # Modelo de Notificación
│   ├── task.py              # Modelo de Tarea y tabla de asociación TaskCategory
│   └── user.py              # Modelo de Usuario
├── repositories/
│   ├── __init__.py          # Exporta los repositorios
│   ├── base_repository.py   # Clase base para repositorios (CRUD genérico)
│   ├── category_repository.py # Repositorio para Categoría
│   ├── notification_repository.py # Repositorio para Notificación
│   ├── task_repository.py   # Repositorio para Tarea
│   └── user_repository.py   # Repositorio para Usuario
├── services/
│   ├── __init__.py          # Exporta los servicios
│   ├── category_service.py  # Lógica de negocio para Categoría
│   ├── notification_service.py # Lógica de negocio para Notificación
│   ├── task_service.py      # Lógica de negocio para Tarea
│   └── user_service.py      # Lógica de negocio para Usuario
├── tests/
│   ├── __init__.py          # Vacío o para importar pruebas
│   ├── test_base.py         # Configuración base para pruebas (DB en memoria)
│   ├── test_category_service.py # Pruebas para CategoryService
│   ├── test_notification_service.py # Pruebas para NotificationService
│   ├── test_task_service.py # Pruebas para TaskService
│   └── test_user_service.py # Pruebas para UserService
├── app_gui.py             # Interfaz grafica de usuario
├── main.py                # Punto de entrada y demostración CRUD
├── populate_data.py       # Script para insertar datos simulados
├── requirements.txt       # Dependencias del proyecto
└── task_manager_ui.ui     # Interfaz de usuario
```

## Tecnologías Utilizadas

* **Python 3.x**

* **SQLAlchemy**: ORM (Object-Relational Mapper)

* **SQLite**: Base de datos ligera basada en archivos

## Configuración e Instalación

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local:

1. **Clona el Repositorio (si aplica) o crea la estructura**:
   Asegúrate de tener la estructura de carpetas y archivos como se muestra arriba. Si recibiste un archivo `.zip`, descomprímelo.

2. **Crea un Entorno Virtual (Recomendado)**:
   Es una buena práctica crear un entorno virtual para aislar las dependencias del proyecto.

   ```bash
   python -m venv venv
3. Activa el Entorno Virtual:
    Windows:

    ```Bash
    .\venv\Scripts\activate.ps1

    Si ocurre un error de permisos
    Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
    
    ```
    Bash
    ```
    source venv/bin/activate
    ```
    Instala las Dependencias:
    Con el entorno virtual activado, instala las bibliotecas necesarias listadas en requirements.txt:

    Bash
    ```
    pip install -r requirements.txt
    ```
    Inicializa la Base de Datos:
    La base de datos SQLite (database.db) se creará automáticamente en el directorio data/ la primera vez que ejecutes main.py o populate_data.py.

    Uso del Proyecto
    Ejecutar la Demostración CRUD
    El archivo main.py proporciona una demostración paso a paso de las operaciones CRUD para cada entidad.

    Asegúrate de que tu entorno virtual esté activado.

    Desde el directorio raíz del proyecto (proyecto/), ejecuta:

    Bash
    ```
    python main.py
    ```
    Observa la salida en la consola para ver cómo se crean, leen, actualizan y eliminan los datos.

    Insertar Datos Simulados
    Puedes usar populate_data.py para llenar tu base de datos con una cantidad considerable de datos de prueba.

    Asegúrate de que tu entorno virtual esté activado.

    Desde el directorio raíz del proyecto (proyecto/), ejecuta:

    Bash
    ```
    python populate_data.py
    ```
    Este script generará usuarios, categorías, tareas y notificaciones aleatorias.

    Ejecución de Pruebas Unitarias
    El proyecto incluye pruebas unitarias para garantizar la correcta funcionalidad de la lógica de negocio. Estas pruebas utilizan una base de datos SQLite en memoria, lo que las hace rápidas y aisladas.

    Asegúrate de que tu entorno virtual esté activado.

    Desde el directorio raíz del proyecto (proyecto/), ejecuta el descubridor de pruebas de unittest:

    Bash
    ```
    python -m unittest discover tests
    python -m unittest .\tests\test_category_service.py
    ```
    Ejecucion de la Aplicación
    Bash
    ```
    python app_gui.py
    ```
    Si todas las pruebas pasan, verás un mensaje "OK". En caso contrario, se mostrarán los detalles de los fallos.

### Lista de Integrantes del Equipo
- Cortez Ponce Brianna Shaquel
- Cruz Salazar Jorge Luis
- Estrada Flores Axel Sebastian
- Hilario Talavera Alexander Daniel






