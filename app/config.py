from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # ProxyMind additions
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str
    groq_api_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str

    class Config:
        env_file = ".env"       
settings = Settings()