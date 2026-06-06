import logging

from pydantic import computed_field
# from sqlalchemy import NullPool

from app.settings.app import AppSettings
from app.settings.envTypes import Engine_Props

class TestAppSettings(AppSettings):
    """
    Test application settings.
    """

    debug: bool = True

    title: str = "[TEST] Conduit API"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env.test"

    @computed_field  # type: ignore
    @property
    def sqlalchemy_engine_props(self) -> Engine_Props:
        return Engine_Props(
            url=self.sql_db_uri,
            echo=False,
            # poolclass=NullPool,
            # isolation_level="AUTOCOMMIT",
        )
