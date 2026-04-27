from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DriftServiceSettings(BaseSettings):
    """Runtime configuration for Supabase-backed drift analysis."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(alias="SUPABASE_SERVICE_ROLE_KEY")

    invoice_extractions_table: str = "invoice_extractions"
    invoice_drift_reports_table: str = "invoice_drift_reports"

    current_window_size: int = 20
    reference_window_size: int = 100

    @property
    def query_limit(self) -> int:
        return self.current_window_size + self.reference_window_size


@lru_cache(maxsize=1)
def get_settings() -> DriftServiceSettings:
    return DriftServiceSettings()
