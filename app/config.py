from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname:str = "postgres"
    database_password:str = "localhost"
    secret_key:str = "67ewjsysudgsytuew"
    class Config:
        env_file = ".env"

settings = Settings()