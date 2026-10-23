# FocusFlow

![status](https://img.shields.io/badge/status-en%20desarrollo-yellow)

Aplicación realizada con TypeScript + React + Python + PostgreSQL que sirve como un gestor de tareas con un Pomodoro "flexible" que busca adaptar sesiones de trabajo efectivas según la tarea / contexto en cuestión, y apoyar al usuario en lograr sus objetivos de forma medible.

### Demo en vivo

Una demostración de la primera versión de la aplicación (gestión de tareas con registro y login) se encuentra en https://frontend-alfy.onrender.com/login, hospedada en la plataforma de Render con el plan gratuito. La documentación del backend se puede consultar en https://backend-l28n.onrender.com/docs

*NOTA*: Dado que se usa el [plan gratuito de Render](https://render.com/docs/free), existen ciertas limitaciones, incluyendo
- Después de 15 minutos de inactividad, el servicio de backend entra en un estado frío. **Render lo reactiva dentro de ~1 minuto**. Es necesario esperar ese minuto para probar bien la demostración.
- El servicio de Postgres gratuito **expira a los 30 días** (creado el 2026-10-23, previsto para caducar el 2026-11-22). Los datos de prueba se pierden al caducar.

Por el momento es una base temporal para demostrar la aplicación, hasta pasar a una opción más estable (AWS u otra de pago).

### Stack tecnológico

- TypeScript + React
- Vite
- Python >=3.13 + FastAPI
- PostgreSQL

### Estructura del repositorio

`backend/` -> Manejo de lógica y datos para la aplicación, mediante Python

`frontend/` -> Código de interfaz del usuario y componentes, mediante TypeScript + React


### Arquitectura

Se puede ejecutar de forma local con Docker Compose (frontend, backend y PostgreSQL). También se encuentra desplegado mediante la plataforma Render, en https://frontend-alfy.onrender.com/login, como paso intermedio antes del despliegue planeado en AWS.

*TODO:* Diseño de la arquitectura AWS; el estado actual está en
[`docs/architecture.md`](docs/architecture.md).

### Levantar la aplicación

*TODO*


### Estado del proyecto

En desarrollo activo - Semana 3 - Primera versión y despliegue
