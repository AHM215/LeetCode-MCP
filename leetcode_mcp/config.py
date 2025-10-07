from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    leetcode_session: str | None = None
    leetcode_csrftoken: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
