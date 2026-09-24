# The Twelve-Factor App — aplicado a FocusFlow

Lectura: https://12factor.net/es/ — mapeo de cada factor a una parte concreta del repo.

| # | Factor | Dónde aplica en FocusFlow |
|---|---|---|
| I | Codebase (1 repo, múltiples deploys) | Se mantiene un único repositorio de versiones de la aplicación (Git, Github), y a partir de ello, poder generar los distintos entornos necesarios (Render, AWS) |
| II | Dependencies (declaradas explícitamente, sin asumir nada del sistema) | El uso de la herramienta de dependencias `uv`, especificando las herramientas necesarias para cada tipo de entorno. Las herramientas son ejecutadas de forma  aislada mediante un venv manejado por `uv`. |
| III | Config (en variables de entorno) | `Settings` (Pydantic Settings) en `backend/src/focusflow_api/config.py`, `.env` fuera del repo, `.env.example` como plantilla. |
| IV | Backing services (tratar la BD como recurso adjunto, intercambiable) | Solicitar entre recursos externos del mismo tipo (como una base de datos) debe ser iguales, independientemente del proveedor (PostgreSQL, MySQL, SQL Server). Se logra mediante referencias por archivos / variables de configuración (`Settings.database_url` |
| V | Build, release, run (etapas separadas) | Asegurar que cada entorno tenga las herramientas necesarias para ejecutar el programa, pero tambien ayuda a evaluar y corregir cambios de una forma más robusta (en caso de error en prod, poder revertir a la versión pasada comprobable en cuestion de segundos). Podria agilizar mediante el CI/CD |
| VI | Processes (stateless, sin estado compartido en memoria) | procesos de fronted-backend deben evitar persistir datos por su cuenta. Las solicitudes y transacciones (HTTP?) que tengan que realizar / procesar sean efimeros, nunca guardar su estado. Para persistir los datos correspondientes, se debe usar el servicio backing como el PostgreSQL  |
| VII | Port binding (la app expone su propio puerto, no depende de un servidor externo inyectado) | Cada servicio debe ser capaz de declarar y arrancar sus procesos por su cuenta, en lugar de un servidor externo / preexistente. Permite portabilidad y contiene lo necesario para ejecutarse sin config. adicional |
| VIII | Concurrency (escalar vía procesos, no threads gigantes) | Podria ser la capacidad para generar más servicios frontend-backend aislados en caso que haya un aumento de tráfico, y duplicar aplicaciones de forma horizontal que se encargue de los usuarios, |
| IX | Disposability (arranque/apagado rápido y sin pérdida de datos) | El backend (create_app y Uvicorn) debe arrancar sin trabajo pesado. Ante la terminación, Uvicorn deja terminar las peticiones en curso antes de salir. El proceso solo maneja datos efimeros. Los datos a persistir viven dentro de la base de datos (PostgreSQL). No se pierde nada con la muerte del proceso. |
| X | Dev/prod parity (mismo stack en todos los entornos) | Postgres real en `docker-compose.yml` desde el día 1 (no SQLite en local + Postgres en prod). Trabjar con la versión de producción disponible siempre que se pueda. |
| XI | Logs (como stream de eventos a stdout, no a archivo) | Los servicios deberia enviar los mensajes de info / error a la salida estandar, mientras que la recopilación, analisis y archivado de estos mensajes debera ser a cargados por el entorno de ejecución (funciones de Render, AWS, etc) |
| XII | Admin processes (tareas one-off corren en el mismo entorno que la app) | Ejecutar tareas / procesos administrativos en el mismo entorno, misma imagen y version. Lanzar una instancia corta con el mismo artefacto. Esto se vería con el uso de Fargate `run-task` |

## Notas

<!-- ✍️ Para los que anotaste "aún no construido": ¿en qué semana de la hoja de ruta esperas que se materialice? -->
