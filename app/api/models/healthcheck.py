from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    version: str = Field(description="Версия сервиса")
    status: bool = Field(description="Статус сервиса")
    service: str = Field(description="Название сервиса")
