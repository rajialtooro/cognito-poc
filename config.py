from pydantic import BaseSettings

# * the app settings


class Settings(BaseSettings):
    app_name: str = "The Solution Orchestrator"
    py_env: str
    free_orch_url: str
    challenges_service_url: str

    class Config:
        env_file = ".env"


# * apply the settings
settings = Settings()
