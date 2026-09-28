import type { ChatResponse, ComputerStatus, HealthResponse } from "../types/api";
import { disable, enable } from "@tauri-apps/plugin-autostart";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

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
