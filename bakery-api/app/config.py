from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Bakery POS API"
    debug: bool = False
    database_url: str

    model_config = {"env_file": ".env"}


settings = Settings()
