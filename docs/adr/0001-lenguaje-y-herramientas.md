# ADR-0001: Lenguaje y herramientas

- **Estado:** Aceptado
- **Fecha:** 2026-09-23

## Contexto

Este proyecto es un ejercicio de aprendizaje individual cuyo fin es comprender el flujo e interacción entre los componentes de una aplicación web full-stack (frontend, API, base de datos, despliegue), desde su conceptualización hasta producción en una plataforma como Render o AWS. Se busca practicar principios de código limpio y seguridad básica (validación de entradas, gestión de secretos, autenticación, HTTPS), y obtener un proyecto de portafolio que refuerce el CV.

Se busca como resultado tener una aplicación desplegada y funcional, con API documentada, autenticación, persistencia de datos, pruebas básicas y un pipeline de despliegue. Se tiene como restricción un plazo de 8 semanas y el uso de capas gratuitas de las plataformas de despliegue.

## Decisión

Se usan Python y TypeScript como lenguajes base del proyecto, junto con uv, FastAPI, Vite y React.

FastAPI resuelve por defecto la validación y el tipado de los datos (aspectos menos relevantes para el aprendizaje) y deja abiertas las piezas que sí se quieren aprender (ORM, migraciones, autenticación). uv gestiona el entorno virtual, las dependencias y el archivo de bloqueo (`uv.lock`) con una sola herramienta. React se elige por tener ya experiencia previa con él y por ser una librería ampliamente usada, lo que también aporta al CV. En conjunto, son herramientas con las que ya se ha trabajado, lo que reduce la fricción y permite enfocarse en los conceptos por aprender.

## Alternativas consideradas

- **Java / Spring:** Con conocimientos, pero hay que reforzar características y peculiaridades del lenguaje, y eso podría restar tiempo para aprender el flujo / ciclo completo de desarrollo.
- **Django (+ DRF):** Framework con "baterías incluidas" para crear aplicaciones completas de una forma más ágil / rápida (ORM, autenticación). Se descarta porque podría ofuscar cómo funciona cada componente / elemento de la aplicación, aunque se tome más tiempo en tener el backend funcionando.
- **Flask:** Microframework minimalista que contiene lo suficiente para manejar solicitudes, y da libertad sobre la implementación del resto (BD, validaciones). Se descarta porque habría que ensamblar las funcionalidades de validación y tipado que FastAPI ofrece de forma automática.
- **pip + venv / poetry (gestión de paquetes):** `pip` + `venv` obliga a combinar herramientas separadas (entorno, instalación y algo extra para fijar versiones). `poetry` cubre lo mismo, pero se elige `uv` por ser más rápido, resolver todo con una sola herramienta y encajar con el ecosistema de Ruff, ya usado en los hooks de pre-commit.
- **Vue:** Buena curva de aprendizaje, pero no se tiene experiencia previa y podría abarcar más tiempo del plazo.
- **Angular:** Framework completo con una curva de aprendizaje muy pronunciada, que podría generar un retraso.

## Consecuencias

- Adaptación rápida a la sintaxis y características de los lenguajes, permitiendo aprender sobre los conceptos / temas relevantes.
- Se refuerzan herramientas conocidas y hay espacio para aprender otras relevantes para el perfil (Docker, Linux, Git).
- Lo que FastAPI y Pydantic resuelven automáticamente (validación, documentación) puede ocultar cómo funcionan por dentro. Se acepta porque no es el foco del aprendizaje.
- Se trabaja con dos lenguajes y dos toolchains (uv, pytest y Ruff en el backend; npm, Vite y oxlint en el frontend). Los tipos de Pydantic y los de TypeScript se declaran por separado y pueden discrepar.
- FastAPI no incluye autenticación, ORM ni migraciones. Se ensamblan a mano, más trabajo que con Django, pero es justo lo que se quiere aprender.
