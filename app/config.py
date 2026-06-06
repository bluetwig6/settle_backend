from functools import lru_cache
from app.settings.envTypes import AppEnvTypes
from app.settings.base import BaseAppSettings
from app.settings.development import DevAppSettings
from app.settings.test import TestAppSettings

environments: dict[str, type[AppEnvTypes]] = {  # type: ignore
    AppEnvTypes.development: DevAppSettings,
    AppEnvTypes.testing: TestAppSettings,
    AppEnvTypes.production: BaseAppSettings,
}

@lru_cache
def get_app_settings() -> BaseAppSettings:
    """
    Return application config.
    """
    app_env = BaseAppSettings().app_env # type: ignore
    config = environments[app_env] # type: ignore
    return config()  # type: ignore