FROM python:3.13-slim
WORKDIR /app


ARG UID=1000

RUN groupadd --gid ${UID} app && \
    useradd --uid ${UID} --gid ${UID} -m --shell /usr/sbin/nologin app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY alembic/ ./alembic/

USER app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "focusflow_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

