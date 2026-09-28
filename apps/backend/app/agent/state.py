from __future__ import annotations

from enum import StrEnum


class AgentState(StrEnum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    PLANNING = "PLANNING"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    @staticmethod
    def is_valid_transition(current: AgentState, next_state: AgentState) -> bool:
        valid: dict[AgentState, set[AgentState]] = {
            AgentState.IDLE: {AgentState.THINKING, AgentState.CANCELLED},
            AgentState.THINKING: {AgentState.PLANNING, AgentState.FAILED, AgentState.CANCELLED},
            AgentState.PLANNING: {AgentState.EXECUTING, AgentState.WAITING_CONFIRMATION, AgentState.FAILED},
            AgentState.WAITING_CONFIRMATION: {AgentState.EXECUTING, AgentState.CANCELLED},
            AgentState.EXECUTING: {AgentState.VERIFYING, AgentState.FAILED, AgentState.CANCELLED},
            AgentState.VERIFYING: {AgentState.COMPLETED, AgentState.FAILED, AgentState.CANCELLED},
            AgentState.COMPLETED: {AgentState.IDLE},
            AgentState.FAILED: {AgentState.IDLE},
            AgentState.CANCELLED: {AgentState.IDLE},
        }
        return next_state in valid.get(current, set())

    @staticmethod
    def transition(current: AgentState, next_state: AgentState) -> AgentState:
        if not AgentState.is_valid_transition(current, next_state):
            raise ValueError(f"Invalid state transition: {current} -> {next_state}")
        return next_state
