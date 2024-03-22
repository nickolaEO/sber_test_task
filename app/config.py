import os
import re
from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="",
    environments=True,
    settings_files=["settings.yml"],
)

PROJECT_PATH = str(Path(__file__).parent.parent.resolve())

with open(os.path.join(PROJECT_PATH, "pyproject.toml"), encoding="utf-8") as file:
    file_data = file.read()
settings.VERSION = re.search(r'version = "(?P<version>\d+.\d+.\d+)"', file_data).group("version")

DB_URL_WITH_ALEMBIC = (
    f"postgresql+psycopg2://{settings.POSTGRES.login}:{settings.POSTGRES.password}@"
    f"{settings.POSTGRES.host}:{settings.POSTGRES.port}/{settings.POSTGRES.database}"
)
