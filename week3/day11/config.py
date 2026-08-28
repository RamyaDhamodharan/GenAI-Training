from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str
    model: str = "qwen/qwen-2.5-7b-instruct"
    temperature: float = 0.0
    request_timeout: float = 30.0

    model_config = SettingsConfigDict(
    env_file="../../.env",
    extra="ignore"
   )


settings = Settings()