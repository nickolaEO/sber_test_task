FROM python:3.10

ARG PROJECT_NAME=sber-test-task
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt update && \
    pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools && \
    pip3 install poetry

WORKDIR /src/app
COPY poetry.lock pyproject.toml /src/app/
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi
COPY . .

CMD python main.py
