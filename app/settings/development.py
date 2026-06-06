import logging
from pydantic import computed_field
from app.settings.app import AppSettings
from app.settings.envTypes import Engine_Props

class DevAppSettings(AppSettings):
    """
    Development application settings.
    """

    debug: bool = True

    title: str = "[DEV] Conduit API"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env.dev"

    @computed_field  # type: ignore
    @property
    def sqlalchemy_engine_props(self) -> Engine_Props:
        return Engine_Props(url=self.sql_db_uri, echo=True)
