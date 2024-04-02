FROM python:3.11-buster AS builder

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
# poetry complains if README.md is not present (there are build benefits to create empty one instead of copying the real one)
RUN touch README.md

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

####################################################################################################

FROM python:3.11-slim-buster AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src ./app/src
COPY checks.yaml ./app/checks.yaml

WORKDIR /app

# to prevent python from buffering output
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]
