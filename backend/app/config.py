from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/jobboard"
    admin_api_key: str = "change-me-in-production"
    cors_origins: str = "*"
    scrape_sleep_seconds: int = 45
    default_results_wanted: int = 20
    default_hours_old: int = 168
    default_sites: str = "indeed,linkedin,naukri,foundit"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def site_list(self) -> list[str]:
        return [s.strip() for s in self.default_sites.split(",") if s.strip()]


settings = Settings()
