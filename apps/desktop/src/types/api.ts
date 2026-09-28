export interface HealthResponse { status: string; service: string; version: string }
export interface ChatRequest { message: string }
export interface ChatResponse { message: string; response?: string }
export interface ToolRequest { tool: string; arguments: Record<string, unknown> }
export interface ToolResult { success: boolean; output?: unknown; error?: string }
export interface PermissionRequest { action: string; risk: "safe" | "confirm" | "block" }
export interface TaskStatus { status: "idle" | "running" | "complete" | "error" }
export interface AgentState { task: TaskStatus; message?: string }
