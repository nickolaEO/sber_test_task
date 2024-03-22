from typing import Union

from sqlalchemy import AsyncAdaptedQueuePool, Pool, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings


class SessionManager:
    def __init__(
        self,
        dialect: str,
        host: str,
        login: str,
        password: str,
        port: Union[str, int],
        database: str,
        service_name: str,
        poolclass: Pool = AsyncAdaptedQueuePool,
        **kwargs,
    ):
        """
        Инициализация подключения к бд
        :param dialect:         диалект
        :param host:            хост
        :param port:            порт
        :param login:           логин
        :param password:        пароль
        :param database:        название базы данных
        :param service_name:    название сервиса
        :param kwargs:          дополнительные параметры подключения
        """
        self.dialect = dialect
        self.login = login
        self.password = password
        self.host = host
        self.port = port
        self.database = database

        self.engine = create_async_engine(
            url=self.db_url,
            connect_args={"server_settings": {"application_name": f"kt-{service_name}"}},
            poolclass=poolclass,
            **kwargs,
        )
        self.autocommit_engine = self.engine.execution_options(isolation_level="AUTOCOMMIT")
        self._transactional_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self._async_session_factory = async_sessionmaker(self.autocommit_engine)

    @property
    def transactional_session(self):
        """
        Транзакционная сессия
        :return:    сессия
        """
        return self._transactional_session

    @property
    def async_session_factory(self):
        """
        Автокоммит сессия
        :return:    сессия
        """
        return self._async_session_factory

    @property
    def db_url(self) -> str:
        """
        URL подключения к бд
        :return:    url
        """
        return f"postgresql+{self.dialect}://{self.login}:{self.password}@{self.host}:{self.port}/{self.database}"

    async def ping(self):
        """
        Пинг к бд
        :return:    None
        """
        async with self.async_session_factory() as session:
            await session.execute(text("SELECT 1;"))
            await session.commit()

        async with self.transactional_session() as session:
            await session.execute(text("SELECT 1;"))
            await session.commit()


session_manager = SessionManager(
    dialect=settings.POSTGRES.dialect,
    host=settings.POSTGRES.host,
    login=settings.POSTGRES.login,
    password=settings.POSTGRES.password,
    port=settings.POSTGRES.port,
    database=settings.POSTGRES.database,
    service_name=settings.NAME,
    poolclass=AsyncAdaptedQueuePool,
)
