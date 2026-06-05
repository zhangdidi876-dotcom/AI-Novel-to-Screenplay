"""应用配置管理"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./screenplay.db"

    # AI 模型配置（主模型）
    ai_base_url: str = "https://api.openai.com/v1"
    ai_api_key: str = ""
    ai_model_name: str = "gpt-4o"

    # 备选模型列表（JSON 字符串，前端可切换）
    ai_models_json: str = "[]"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
