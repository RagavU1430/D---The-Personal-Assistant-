JARVIS-X treats model output as untrusted data. Tool names and arguments are accepted only through the registry and Pydantic schemas, then passed through the permission engine and `ToolExecutor`. There is no direct model path to shell, Python, filesystem mutation, browser automation, or process control.

`SAFE` tools can run automatically, `CONFIRM` tools return a confirmation contract without execution, and `BLOCK` tools are rejected. Every execution attempt is audit logged with tool, risk, decision, result, duration, and error code; sensitive argument values are not recorded.

Phase 2 enables only read-only system information tools. Terminal, browser, computer-control, deletion, messaging, and remote-access capabilities remain unavailable until later phases receive explicit policy and tests.

Phase 3 computer control remains structured and allowlisted. Applications are selected by configured names, never executable paths from model output. Mouse coordinates and keyboard keys are validated, text entry and window closing require confirmation, and the emergency stop disables new controller actions until explicitly resumed. Windows startup uses the per-user Startup folder only; no hidden persistence or unrelated startup changes are created.
# Security

Phase 0 uses explicit `SAFE`, `CONFIRM`, and `BLOCK` risk decisions plus an audit logger interface. No Phase 1+ operating-system capability is registered or exposed.

## Permission model

- `SAFE`: low-risk operations with no approval required
- `CONFIRM`: actions requiring explicit user approval
- `BLOCK`: actions prohibited by policy or architecture

## Secret handling

Secrets are loaded from environment configuration and excluded from Git. Logs redact fields containing keys, tokens, passwords, and secrets.

## Future computer-control restrictions

Future computer, terminal, browser, and filesystem tools must validate structured inputs, remain allowlisted, use permissions, and support an emergency stop before execution.
