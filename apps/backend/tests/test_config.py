from app.config import Settings


def test_settings_do_not_require_provider_keys() -> None:
    config = Settings()
    assert config.app_name == "D - The personal Assistant"
    assert config.openai_api_key is None
    assert config.allowed_cors_origins
