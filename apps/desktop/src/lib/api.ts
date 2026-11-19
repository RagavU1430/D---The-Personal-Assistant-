import type {
  ActiveWindowResponse,
  ChatResponse,
  ComputerStatus,
  HealthResponse,
  ToolMetadata,
  ToolResult,
  WindowInfo,
} from "../types/api";
import { disable, enable } from "@tauri-apps/plugin-autostart";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8001/api/v1";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error("Backend unavailable");
  return response.json() as Promise<HealthResponse>;
}

export async function sendChat(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) throw new Error("Assistant unavailable");
  return response.json() as Promise<ChatResponse>;
}

export async function getComputerStatus(): Promise<ComputerStatus> {
  const response = await fetch(`${API_BASE}/computer/status`);
  if (!response.ok) throw new Error("Computer status unavailable");
  return response.json() as Promise<ComputerStatus>;
}

export async function setComputerControl(enabled: boolean): Promise<void> {
  const response = await fetch(`${API_BASE}/computer/${enabled ? "resume" : "stop"}`, { method: "POST" });
  if (!response.ok) throw new Error("Unable to update computer control");
}

export async function setStartup(enabled: boolean): Promise<void> {
  const response = await fetch(`${API_BASE}/startup?enabled=${enabled}`, { method: "POST" });
  if (!response.ok) throw new Error("Unable to update startup setting");
  if ("__TAURI_INTERNALS__" in window) {
    if (enabled) await enable();
    else await disable();
  }
}

export async function getTools(): Promise<{ tools: ToolMetadata[] }> {
  const response = await fetch(`${API_BASE}/tools`);
  if (!response.ok) throw new Error("Tools unavailable");
  return response.json() as Promise<{ tools: ToolMetadata[] }>;
}

export async function executeTool(tool: string, args: Record<string, any> = {}): Promise<ToolResult> {
  const response = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, arguments: args }),
  });
  if (!response.ok) throw new Error(`Execution of ${tool} failed`);
  return response.json() as Promise<ToolResult>;
}

export async function getWindows(): Promise<{ windows: WindowInfo[] }> {
  const response = await fetch(`${API_BASE}/windows`);
  if (!response.ok) throw new Error("Windows listing unavailable");
  return response.json() as Promise<{ windows: WindowInfo[] }>;
}

export async function getActiveWindow(): Promise<ActiveWindowResponse> {
  const response = await fetch(`${API_BASE}/computer/active-window`);
  if (!response.ok) throw new Error("Active window query failed");
  return response.json() as Promise<ActiveWindowResponse>;
}

export async function takeScreenshot(): Promise<ToolResult> {
  const response = await fetch(`${API_BASE}/computer/screenshot`, { method: "POST" });
  if (!response.ok) throw new Error("Screenshot request failed");
  return response.json() as Promise<ToolResult>;
}

// Phase 5 — Terminal / Developer JARVIS API
export interface GitCommandInput {
  subcommand: string;
  args?: string[];
  working_dir?: string;
}

export interface TestCommandInput {
  framework?: string;
  args?: string[];
  working_dir?: string;
}

export interface LogAnalysisInput {
  content: string;
  max_findings?: number;
}

export interface ExecuteCommandInput {
  command: string;
  args?: string[];
  working_dir?: string;
}

export interface TerminalStatusResponse {
  enabled: boolean;
  allowlist: string[];
  working_dirs: string[];
  max_output_bytes: number;
  git_subcommands: string[];
}

export async function runGitCommand(input: GitCommandInput): Promise<ToolResult> {
  const response = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool: "git", arguments: input }),
  });
  if (!response.ok) throw new Error("Git command failed");
  return response.json() as Promise<ToolResult>;
}

export async function runTests(input: TestCommandInput): Promise<ToolResult> {
  const response = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool: "run_tests", arguments: input }),
  });
  if (!response.ok) throw new Error("Test execution failed");
  return response.json() as Promise<ToolResult>;
}

export async function analyzeLogs(input: LogAnalysisInput): Promise<ToolResult> {
  const response = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool: "analyze_logs", arguments: input }),
  });
  if (!response.ok) throw new Error("Log analysis failed");
  return response.json() as Promise<ToolResult>;
}

export async function executeTerminalCommand(input: ExecuteCommandInput): Promise<ToolResult> {
  const response = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool: "execute_command", arguments: input }),
  });
  if (!response.ok) throw new Error("Command execution failed");
  return response.json() as Promise<ToolResult>;
}

export async function getTerminalStatus(): Promise<TerminalStatusResponse> {
  const response = await fetch(`${API_BASE}/tools/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool: "terminal_status", arguments: {} }),
  });
  if (!response.ok) throw new Error("Terminal status unavailable");
  const result = await response.json() as ToolResult;
  return result.data as TerminalStatusResponse;
}
