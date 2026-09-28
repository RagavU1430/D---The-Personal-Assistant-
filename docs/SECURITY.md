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
