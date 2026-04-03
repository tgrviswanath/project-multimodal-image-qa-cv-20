from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "Multimodal Image QA CV Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    BLIP_MODEL: str = "Salesforce/blip-vqa-base"
    MAX_IMAGE_SIZE: int = 1280

    class Config:
        env_file = ".env"


settings = Settings()
