from typing_extensions import TypedDict
from sqlalchemy import URL


class AppEnvTypes:
  """
  Available application environments.
  """

  production = "prod"
  development = "dev"
  testing = "test"

class Engine_Props(TypedDict):
    url: URL
    echo: bool