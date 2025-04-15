FROM python:3.11-alpine

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN apk add --no-cache --virtual .deps musl-dev libev-dev gcc \
    && pip install --upgrade pip --no-cache-dir \
    && pip install poetry --no-cache-dir \
    && poetry config virtualenvs.create false \
    && poetry install --extras bjoern --no-root --without dev \
    && pip uninstall -y poetry \
    && apk del .deps \
    && apk add --no-cache libev

COPY . .

EXPOSE 80

CMD ["python", "run.py", "0.0.0.0", "80"]
