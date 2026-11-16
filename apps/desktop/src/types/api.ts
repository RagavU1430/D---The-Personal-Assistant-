export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ComputerStatus {
  assistant: string;
  status: string;
  computer_control: boolean;
  tool_system: boolean;
  ai_provider: boolean;
  startup_enabled: boolean;
  background_mode: boolean;
}

export interface ToolMetadata {
  name: string;
  description: string;
  category: string;
  version: string;
  risk: "safe" | "confirm" | "block";
  enabled: boolean;
}

export interface WindowInfo {
  title: string;
  process?: string;
  state?: string;
}

export interface ActiveWindowResponse {
  window: WindowInfo | null;
  error_code?: string;
}

export interface ToolResult {
  success: boolean;
  tool: string;
  data?: any;
  output?: any;
  error_code?: string;
  message: string;
  execution_time_ms: number;
}

export interface PlanStep {
  id: string;
  description: string;
  action_type: string;
  tool?: string;
  arguments?: Record<string, any>;
}

export interface AgentPlan {
  goal: string;
  steps: PlanStep[];
}

export interface ChatResponse {
  message: string;
  state: string;
  intent?: string;
  plan?: AgentPlan | null;
  tool_results: ToolResult[];
}

export interface ChatMessageItem {
  id: string;
  sender: "user" | "assistant" | "system" | "tool";
  text: string;
  timestamp: string;
  intent?: string;
  toolResult?: ToolResult;
  plan?: AgentPlan | null;
}
