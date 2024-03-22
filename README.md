# Установка и запуск проекта

## Переменные окружения

Убедитесь, что вы определили переменные окружения. 
В данном проекте используется файл конфигурации /config/settings.yml, в котором указаны все параметры,
необходимые для работы сервиса.
Параметры для подключения к БД устанавливаются в этом месте:
```yml
POSTGRES:
    dialect: asyncpg
    host: db # название контейнера с БД
    port: 5432
    login: postgres
    password: postgres
    database: postgres
```  

Создайте файл .env в корне проекта и укажите параметры, необходимые для развертывания контейнера с БД:
```dotenv
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## Локальная установка

Проект можно развернуть из исходников, либо через Docker

### Развертывание из исходников
1. ```bash
   git clone https://github.com/nickolaEO/sber_test_task.git
   ```
2. ```bash
   poetry shell
   ```
3. ```bash
   poetry install
   ```
4. ```bash
   alembic upgrade head
   ```

### Запуск
```bash
python main.py
 ```

## Запуск контейнера

1. ```bash
   git clone https://github.com/nickolaEO/sber_test_task.git
   ```
2. ```bash
   docker-compose up -d --build
   ```

## Доступ к api


Сервис разворачивается на адресе 0.0.0.0:80.

Api документация доступна по 0.0.0.0:80/docs.