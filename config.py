from pydantic import BaseSettings

# * the app settings


class Settings(BaseSettings):
    app_name: str = "The Solution Orchestrator"
    py_env: str
    free_orch_url: str
    challenges_service_url: str
    courses_service_url: str
    auth_service_url: str
    fs_compiler_service_url: str

    class Config:
        env_file = ".env"


# * apply the settings
settings = Settings()
