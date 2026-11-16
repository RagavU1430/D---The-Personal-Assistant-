import { useEffect, useState } from "react";
import {
  Cpu,
  HardDrive,
  Clock,
  Shield,
  Activity,
  Play,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Sliders,
} from "lucide-react";
import { executeTool, getTools } from "../lib/api";
import type { ToolMetadata, ToolResult } from "../types/api";

export function SafeToolsPanel() {
  const [tools, setTools] = useState<ToolMetadata[]>([]);
  const [telemetry, setTelemetry] = useState<{
    cpu?: number;
    memory?: { total: number; used: number; percentage: number };
    disk?: { total: number; used: number; percentage: number };
    time?: string;
  }>({});
  const [selectedTool, setSelectedTool] = useState<ToolMetadata | null>(null);
  const [executing, setExecuting] = useState(false);
  const [lastResult, setLastResult] = useState<ToolResult | null>(null);
  const [loading, setLoading] = useState(false);

  const refreshAll = async () => {
    setLoading(true);
    try {
      const toolList = await getTools();
      setTools(toolList.tools || []);

      // Poll safe system stats directly via registered safe tools
      const [cpuRes, memRes, timeRes] = await Promise.all([
        executeTool("cpu_usage", {}),
        executeTool("memory_usage", {}),
        executeTool("current_time", {}),
      ]);

      setTelemetry({
        cpu: cpuRes.data?.percentage,
        memory: memRes.data,
        time: timeRes.data?.formatted,
      });
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 10000);
    return () => clearInterval(interval);
  }, []);

  const runTool = async (toolName: string) => {
    setExecuting(true);
    setLastResult(null);
    try {
      const res = await executeTool(toolName, {});
      setLastResult(res);
    } catch (err: any) {
      setLastResult({
        success: false,
        tool: toolName,
        message: err.message || "Execution failed",
        execution_time_ms: 0,
      });
    } finally {
      setExecuting(false);
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "safe":
        return <span className="rounded bg-emerald-950/80 px-2 py-0.5 text-[10px] font-mono text-emerald-300 border border-emerald-800/50">SAFE</span>;
      case "confirm":
        return <span className="rounded bg-amber-950/80 px-2 py-0.5 text-[10px] font-mono text-amber-300 border border-amber-800/50">CONFIRM</span>;
      case "block":
        return <span className="rounded bg-rose-950/80 px-2 py-0.5 text-[10px] font-mono text-rose-300 border border-rose-800/50">BLOCK</span>;
      default:
        return <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono text-slate-300">{risk}</span>;
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Real-time Telemetry Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* CPU */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-4 shadow-md font-mono">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5"><Cpu size={14} className="text-cyan-400" /> CPU USAGE</span>
            <span className="text-cyan-300 font-bold">{telemetry.cpu !== undefined ? `${telemetry.cpu}%` : "--"}</span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500"
              style={{ width: `${Math.min(telemetry.cpu || 0, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Memory */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-4 shadow-md font-mono">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5"><Activity size={14} className="text-emerald-400" /> RAM USAGE</span>
            <span className="text-emerald-300 font-bold">
              {telemetry.memory?.percentage !== undefined ? `${telemetry.memory.percentage}%` : "--"}
            </span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-amber-400 transition-all duration-500"
              style={{ width: `${Math.min(telemetry.memory?.percentage || 0, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Disk */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-4 shadow-md font-mono">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5"><HardDrive size={14} className="text-indigo-400" /> STORAGE</span>
            <span className="text-indigo-300 font-bold">OS ROOT</span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
            <div className="h-full bg-indigo-500 w-2/5"></div>
          </div>
        </div>

        {/* Clock */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-4 shadow-md font-mono">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span className="flex items-center gap-1.5"><Clock size={14} className="text-cyan-400" /> SYSTEM CLOCK</span>
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
          </div>
          <p className="text-xs font-bold text-cyan-100 truncate">{telemetry.time || "Fetching time..."}</p>
        </div>
      </div>

      {/* Tools Directory */}
      <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
        <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
          <div>
            <div className="flex items-center gap-2 text-cyan-300 font-mono text-xs font-bold uppercase tracking-wider">
              <Shield size={16} />
              <span>Registered Safe Tools Directory ({tools.length})</span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Every tool executes inside a timeout-bounded sandbox with Pydantic validation and audit logging.
            </p>
          </div>
          <button
            type="button"
            onClick={refreshAll}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg border border-cyan-800/50 bg-cyan-950/40 px-3 py-1.5 text-xs font-mono text-cyan-300 hover:bg-cyan-900/50 transition"
          >
            <RotateCw size={13} className={loading ? "animate-spin" : ""} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {tools.map((tool) => (
            <div
              key={tool.name}
              className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-950/60 p-4 transition hover:border-cyan-700/50 hover:bg-slate-950/90"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-xs font-mono font-bold text-cyan-200">{tool.name}</span>
                  {getRiskBadge(tool.risk)}
                </div>
                <p className="text-[11px] font-mono text-slate-400 leading-relaxed mb-3">
                  {tool.description}
                </p>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-[10px] font-mono text-slate-500">
                <span>Cat: {tool.category}</span>
                <button
                  type="button"
                  onClick={() => runTool(tool.name)}
                  disabled={executing || tool.risk === "confirm"}
                  title={tool.risk === "confirm" ? "Requires conversational confirmation" : "Execute tool"}
                  className="flex items-center gap-1 rounded bg-cyan-950 px-2.5 py-1 text-cyan-300 hover:bg-cyan-900 border border-cyan-800/40 disabled:opacity-40 transition"
                >
                  <Play size={10} />
                  <span>{tool.risk === "confirm" ? "Needs Confirm" : "Run"}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Execution Output Console */}
      {lastResult && (
        <div className="rounded-xl border border-cyan-800/80 bg-slate-950/90 p-5 shadow-xl space-y-3 font-mono">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              {lastResult.success ? (
                <CheckCircle2 size={16} className="text-emerald-400" />
              ) : (
                <AlertTriangle size={16} className="text-amber-400" />
              )}
              <span className="text-xs font-bold text-cyan-200">
                EXECUTION OUTPUT: {lastResult.tool}
              </span>
            </div>
            <span className="text-[10px] text-slate-400">{lastResult.execution_time_ms}ms</span>
          </div>

          <p className="text-xs text-slate-300">{lastResult.message}</p>

          {lastResult.data && (
            <div className="rounded-lg bg-slate-900/90 p-3 text-xs text-cyan-300 overflow-x-auto max-h-48">
              <pre>{JSON.stringify(lastResult.data, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
