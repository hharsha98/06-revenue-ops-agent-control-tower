from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RevenueOps Agent Control Tower"
    environment: str = "local"
    autonomy_mode: str = "sandbox"
    database_url: str = "postgresql+psycopg://revenueops:revenueops@localhost:5432/revenueops"
    redis_url: str = "redis://localhost:6379/0"
    llm_provider: str = "gemini"
    llm_model: str = "gemini/gemini-2.0-flash"
    allowed_email_domains: str = "sandbox.example.com"
    allowed_slack_channels: str = "demo-alerts"
    allowed_github_repos: str = "demo/revenueops-agent-control-tower"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

