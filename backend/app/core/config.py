from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    MIN_CLUSTER_SIZE: int = 2
    DBSCAN_EPS: float = 0.3
    OLLAMA_MODEL: str = "phi4-mini"
    
    class Config:
        env_prefix = "APP_"

settings = Settings()
