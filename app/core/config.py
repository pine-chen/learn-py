from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    配置类
    """

    app_name: str = "Frontend Agent Workflow Platform"
    env: str = "dev"
    api_prefix: str = ""


settings: Settings = Settings()

__all__ = ["Settings", "settings"]
