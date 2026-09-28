export interface HealthResponse { status: string; service: string; version: string }
export interface ChatRequest { message: string }
export interface ChatResponse { response: string; task?: TaskStatus }
export interface ToolRequest { tool: string; arguments: Record<string, unknown> }
export interface ToolResult { success: boolean; output?: unknown; error?: string }
export interface PermissionRequest { action: string; risk: "safe" | "confirm" | "block" }
export interface TaskStatus { status: "idle" | "running" | "complete" | "error"; message?: string }
export interface AgentState { task: TaskStatus }
