import pytest

from app.lifecycle import DApplicationLifecycle, RuntimeState
from app.startup import InMemoryStartupManager


@pytest.mark.asyncio
async def test_lifecycle_startup_and_graceful_shutdown() -> None:
    startup = InMemoryStartupManager()
    lifecycle = DApplicationLifecycle(startup_manager=startup)

    await lifecycle.startup()
    assert lifecycle.state == RuntimeState.READY
    assert lifecycle.health()["tool_system"] is True

    await lifecycle.shutdown()
    assert lifecycle.state == RuntimeState.STOPPED


@pytest.mark.asyncio
async def test_startup_setting_is_user_controlled() -> None:
    startup = InMemoryStartupManager()
    lifecycle = DApplicationLifecycle(startup_manager=startup)

    await lifecycle.set_start_with_windows(False)

    assert startup.enabled is False
