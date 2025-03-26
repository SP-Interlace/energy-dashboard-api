FROM python:3.11

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry --no-cache-dir \
  && poetry config virtualenvs.create false \
  && poetry install --no-root --without dev \
  && pip uninstall -y poetry

COPY . .

EXPOSE 80

CMD ["python", "run.py", "0.0.0.0", "80"]
