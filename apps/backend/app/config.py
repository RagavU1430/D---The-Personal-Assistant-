from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "D - The personal Assistant"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "production"] = "development"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    database_url: str = "sqlite:///./d.db"
    ai_provider: str = ""
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    nvidia_nim_api_key: str | None = None
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    ai_model: str = ""
    ai_timeout_seconds: float = Field(default=12.0, gt=0, le=60)
    provider_cooldown_seconds: float = Field(default=30.0, ge=0, le=3600)
    autonomy_level: int = Field(default=1, ge=0, le=4)
    enable_browser: bool = False
    enable_computer_control: bool = True
    enable_terminal: bool = False
    enable_voice: bool = False
    enable_system_tools: bool = True
    start_with_windows: bool = True
    background_mode: bool = True
    launch_ui_at_startup: bool = False
    autonomous_mode: bool = False
    application_allowlist: str = (
        "notepad=notepad.exe,calculator=calc.exe,file_explorer=explorer.exe,"
        "vscode=code.exe,chrome=chrome.exe,edge=msedge.exe"
    )
    tool_timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def application_map(self) -> dict[str, str]:
        applications: dict[str, str] = {}
        for entry in self.application_allowlist.split(","):
            name, separator, executable = entry.partition("=")
            if separator and name.strip() and executable.strip():
                applications[name.strip().lower()] = executable.strip()
        return applications


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
