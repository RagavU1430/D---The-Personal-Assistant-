from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

Coordinate = Annotated[int, Field(ge=0, le=10000)]
_ALLOWED_KEYS = {
    "ENTER", "ESC", "ESCAPE", "TAB", "SPACE", "BACKSPACE", "DELETE", "UP", "DOWN", "LEFT", "RIGHT",
    "HOME", "END", "PAGEUP", "PAGEDOWN", "CTRL", "ALT", "SHIFT", "WIN", "A", "B", "C", "D", "S",
}


class ApplicationInput(BaseModel):
    application: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9_-]+$")


class WindowInput(BaseModel):
    title: str = Field(min_length=1, max_length=256)


class MouseInput(BaseModel):
    x: Coordinate
    y: Coordinate


class TypeTextInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class KeyInput(BaseModel):
    key: str

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in _ALLOWED_KEYS:
            raise ValueError("Unsupported key.")
        return normalized


class HotkeyInput(BaseModel):
    keys: list[str] = Field(min_length=2, max_length=4)

    @field_validator("keys")
    @classmethod
    def validate_keys(cls, values: list[str]) -> list[str]:
        normalized = [value.upper() for value in values]
        if any(value not in _ALLOWED_KEYS for value in normalized):
            raise ValueError("Unsupported key.")
        return normalized


class EmptyComputerInput(BaseModel):
    pass
