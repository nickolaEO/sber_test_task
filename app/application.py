import logging
import logging.config

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.healthcheck import health_check_router
from app.api.routers.system_items import system_items_router
from app.config import settings
from app.exception_handlers import validation_exception_handler


class Server:
    """
    Класс для создания приложения сервиса
    """

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        logging_config: dict,
        cors_config: dict,
        routers: list[APIRouter] = None,
        start_callbacks: list[callable] = None,
        stop_callbacks: list[callable] = None,
        exception_handlers: dict = None,
        middlewares: list[Middleware] = None,
    ) -> None:
        self.name = name
        self.version = version
        self.description = description

        self.logging_config = logging_config
        self.cors_config = cors_config

        self.routers = routers or []
        self.start_callbacks = start_callbacks or []
        self.stop_callbacks = stop_callbacks or []
        self.exception_handlers = exception_handlers or {}
        self.middlewares = middlewares or []
        self.app = FastAPI(
            version=name,
            title=version,
            description=description,
        )
        self._init_logger()
        self._init_cors()
        self._init_start_callbacks()
        self._init_stop_callbacks()
        self._init_routers()
        self._init_middlewares()
        self._init_exception_handler()

    def _init_routers(self):
        for router in self.routers:
            self.app.include_router(router)
        logging.info("Инициализация routers прошла успешно")

    def _init_exception_handler(self):
        for handler, exc_class in self.exception_handlers.items():
            self.app.add_exception_handler(exc_class, handler)
        logging.info("Инициализация exception_handlers прошла успешно")

    def _init_middlewares(self):
        for middleware in self.middlewares:
            self.app.add_middleware(middleware.middleware_class, dispatch=middleware)
        logging.info("Инициализация middlewares прошла успешно")

    def _init_logger(self) -> None:
        logging.config.dictConfig(self.logging_config)
        logging.info("Инициализация logger прошла успешно")

    def _init_cors(self) -> None:
        self.app.add_middleware(CORSMiddleware, **self.cors_config)
        logging.info("Инициализация cors прошла успешно")

    def _init_start_callbacks(self):
        for callback in self.start_callbacks:
            self.app.on_event("startup")(callback)
        logging.info("Инициализация startup callbacks прошла успешно")

    def _init_stop_callbacks(self):
        for callback in self.stop_callbacks:
            self.app.on_event("shutdown")(callback)
        logging.info("Инициализация shutdown callbacks прошла успешно")


app = Server(
    name=settings.NAME,
    version=settings.VERSION,
    description="Сервис облачного хранения файлов",
    logging_config=settings.LOGGING,
    cors_config=settings.CORS,
    exception_handlers={validation_exception_handler: RequestValidationError},
    routers=[
        health_check_router,
        system_items_router,
    ],
).app
