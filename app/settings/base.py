from pydantic import computed_field
from pydantic_settings import BaseSettings
from app.settings.envTypes import AppEnvTypes
from app.settings.envTypes import Engine_Props
from sqlalchemy import URL



class BaseAppSettings(BaseSettings):
    
    # read this from command line argument
    app_env: str = AppEnvTypes.production

    jwt_secret_key: str
    jwt_access_token_expire_minutes: int
    jwt_algorithm: str

    postgres_user: str
    postgres_password: str
    postgres_port: int
    postgres_db: str
    postgres_host: str

    class Config:  
        env_file = ".env"

    @computed_field  # type: ignore
    @property
    def sql_db_uri(self) -> URL:
        return URL.create(
            drivername="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )
        

    @computed_field  # type: ignore
    @property
    def sqlalchemy_engine_props(self) -> Engine_Props:
        return Engine_Props(url=self.sql_db_uri, echo=False)