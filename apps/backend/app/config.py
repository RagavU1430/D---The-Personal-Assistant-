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
    port: int = Field(default=8001, ge=1, le=65535)
    database_url: str = "sqlite:///./d.db"
    ai_provider: str = ""
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    nvidia_nim_api_key: str | None = None
    nvidia_nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    ai_model: str = ""
    ai_models: str = ""
    ai_timeout_seconds: float = Field(default=12.0, gt=0, le=60)
    provider_cooldown_seconds: float = Field(default=30.0, ge=0, le=3600)

    # Custom AI providers (OpenAI-compatible endpoints)
    # Format: "provider1=base_url,api_key,model|provider2=base_url,api_key,model"
    custom_ai_providers: str = ""
    autonomy_level: int = Field(default=1, ge=0, le=4)
    enable_browser: bool = False
    enable_computer_control: bool = True
    enable_voice: bool = True
    enable_system_tools: bool = True

    # Phase 4 — File System Intelligence
    enable_file_tools: bool = False
    approved_file_roots: str = ""
    protected_file_roots: str = ""
    max_file_size_mb: int = Field(default=100, ge=1, le=1000)
    large_file_threshold_mb: int = Field(default=50, ge=1, le=10000)

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
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"

    # Phase 5 — Terminal / Developer JARVIS tools
    enable_terminal_tools: bool = False
    approved_working_roots: str = ""
    command_allowlist: str = (
        "git,pytest,python,node,npm,cargo,go,dotnet,make,cmake,ruff,mypy,black"
    )
    git_allowed_subcommands: str = "status,diff,log,branch,commit,push"
    terminal_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    max_output_bytes: int = Field(default=1_000_000, ge=1024, le=50_000_000)

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

    @property
    def approved_working_roots_list(self) -> list[str]:
        if not self.approved_working_roots.strip():
            return []
        return [d.strip() for d in self.approved_working_roots.split(",") if d.strip()]

    @property
    def command_allowlist_set(self) -> set[str]:
        return {c.strip().lower() for c in self.command_allowlist.split(",") if c.strip()}

    @property
    def git_allowed_subcommands_set(self) -> set[str]:
        return {s.strip().lower() for s in self.git_allowed_subcommands.split(",") if s.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
