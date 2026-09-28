export interface HealthResponse { status: string; service: string; version: string }
export interface ComputerStatus { assistant: string; status: string; computer_control: boolean; tool_system: boolean; ai_provider: boolean; startup_enabled: boolean; background_mode: boolean }
export interface ChatRequest { message: string }
export interface ToolResult { success: boolean; tool: string; data?: unknown; error_code?: string; message: string; execution_time_ms: number }
export interface ChatResponse { message: string; state: string; intent?: string; plan?: unknown; tool_results: ToolResult[] }
export interface ToolRequest { tool: string; arguments: Record<string, unknown> }
export interface PermissionRequest { action: string; risk: "safe" | "confirm" | "block" }
export interface TaskStatus { status: "idle" | "running" | "complete" | "error" }
export interface AgentState { task: TaskStatus; message?: string }
