# ADR-0002: Base de datos y acceso a datos

- **Estado:** Aceptado
- **Fecha:** 2026-09-25

## Contexto

FocusFlow guarda datos con relaciones claras (usuarios, proyectos, categorías, etiquetas, tareas), con integridad referencial y consultas de agregación para el dashboard de analítica. Además, el objetivo de aprendizaje incluye migraciones versionadas y el despliegue con una base de datos gestionada (Render y luego RDS en AWS).

Restricciones: uso de las capas gratuitas de las plataformas de despliegue (Render, AWS) y proyecto individual. La prioridad es el aprendizaje y la simplicidad por encima del rendimiento.

## Decisión

- **Base de datos: PostgreSQL** (en local, `postgres:16-alpine` vía Docker Compose). Es relacional, soporta `ENUM` nativos y agregaciones, y está disponible como servicio gestionado en Render y en AWS (RDS), por lo que el mismo motor sirve en todos los entornos.
- **ORM: SQLAlchemy 2.0 síncrono** (estilo declarativo con `Mapped` / `mapped_column`) + **Alembic** para migraciones. Se elige implementar el ORM de forma síncrona porque async no acelera las consultas: solo libera al servidor mientras espera I/O. Con un MVP de poca concurrencia esa ganancia no compensa la complejidad extra (fixtures async, riesgo de cargas perezosas fuera de contexto). FastAPI ejecuta los endpoints `def` en un threadpool, así que un endpoint síncrono no bloquea el resto. Es una decisión consciente y reversible.
- **Driver: `psycopg[binary]` (psycopg 3)**, con URL `postgresql+psycopg://`. Es el driver moderno de Postgres para Python y soporta modo síncrono y async, lo que deja abierta la migración a async sin cambiar de driver.
- **ENUM de Python → `ENUM` nativo de Postgres con `values_callable`**. Por defecto SQLAlchemy persiste el `.name` del miembro (p. ej. `HIGH`). Por eso se usa un helper `enum_values()` para persistir el `.value` en minúsculas y así el contrato de la base de datos no depende del nombre interno de la clase Python.

## Alternativas consideradas

- **SQLite:** Cero configuración, pero difiere de producción (tipos, `ENUM`, concurrencia) y no permite practicar el despliegue con una base gestionada.
- **MySQL / MariaDB:** Válida técnicamente, pero Postgres es el estándar de RDS/Render que se quiere practicar.
- **MongoDB (documental):** El modelo a seguir es de tipo relacional (N:M entre tareas y etiquetas, claves foráneas). Modelarlo en documentos perdería integridad referencial.
- **SQLAlchemy asíncrono (`AsyncSession`):** Es lo que se recomienda con FastAPI cuando hay mucha concurrencia de I/O. Se pospone: más superficie de fallo en tests y sin beneficio medible en este MVP.
- **SQLModel / Django ORM:** SQLModel oculta parte de lo que se quiere aprender (mapeo y sesiones de SQLAlchemy); Django ORM no encaja con FastAPI (ver ADR-0001).
- **`psycopg2`:** Driver clásico y muy extendido, pero solo síncrono; psycopg 3 es su sucesor.

## Consecuencias

- Un solo motor en todos los entornos (local, Render, RDS), para minimizar errores al desplegar.
- Se practican migraciones reales con Alembic, incluyendo su revisión manual (p. ej. `downgrade()` debe borrar los tipos `ENUM`, que autogenerate no elimina).
- Cada `ENUM` nuevo o modificado exige una migración cuidadosa: cambiar los valores de un `ENUM` de Postgres no es trivial.
- Si más adelante se necesita alta concurrencia, migrar a `AsyncSession` implica reescribir el acceso a datos y los tests; se acepta ese costo diferido.
- Se reevaluará el uso de async si el proyecto llega a depender de un recurso externo lento (p. ej. una estrategia de recomendación con LLM) o si la concurrencia real lo exige.
