# Arquitectura de FocusFlow

> **Estado:** Borrador. La sección "Hoy" describe lo que existe; "Objetivo en AWS" es el destino a cumplir.

## Progresión de despliegue

`local (Docker Compose)` → `Render (PaaS)` → `AWS manual (ECS Fargate)` → `AWS con CDK (IaC)`

## Hoy: local con Docker Compose

| Servicio | Rol | Puerto |
|---|---|---|
| `frontend` | Vite + React + TS en modo desarrollo (hot-reload) | 5173 |
| `backend` | FastAPI (Uvicorn) | 8000 |
| `postgres` | PostgreSQL 16 | interno |

La configuración llega por variables de entorno (`.env`), según el factor III de 12-factor.

## Objetivo en AWS

> **TODO.**
