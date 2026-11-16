import { useState } from "react";
import { Settings, Power, Shield, Sliders, Cpu, CheckCircle2 } from "lucide-react";
import { setStartup, setComputerControl } from "../lib/api";

interface SettingsPanelProps {
  computerEnabled: boolean;
  startupEnabled: boolean;
  onComputerToggle: () => void;
  onStartupToggle: () => void;
}

export function SettingsPanel({
  computerEnabled,
  startupEnabled,
  onComputerToggle,
  onStartupToggle,
}: SettingsPanelProps) {
  const [autonomyLevel, setAutonomyLevel] = useState<number>(1);

  const autonomyLevels = [
    { level: 0, title: "L0 - Advisory", desc: "No tool execution; suggestions and guidance only." },
    { level: 1, title: "L1 - Supervised (Default)", desc: "SAFE tools run automatically; stateful tools require confirmation." },
    { level: 2, title: "L2 - Semi-Autonomous", desc: "Pre-approved automation flows with active user logging." },
    { level: 3, title: "L3 - High Autonomy", desc: "Reserved for future phases with verified boundaries." },
    { level: 4, title: "L4 - Autonomous", desc: "Unrestricted autonomous agent operations (Strictly disabled)." },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Title */}
      <div className="flex items-center gap-2 border-b border-cyan-950 pb-4">
        <Settings size={18} className="text-cyan-400" />
        <h3 className="text-sm font-bold font-mono text-cyan-200 uppercase tracking-wider">
          Runtime Configuration & Safety Governance
        </h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Startup & Always-On Runtime */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
            <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
              Windows Startup & Background Mode
            </span>
            <Power size={16} className={startupEnabled ? "text-emerald-400" : "text-slate-500"} />
          </div>

          <p className="text-xs font-mono text-slate-300 leading-relaxed">
            Configure D to start with Windows. Uses a clean, user-visible <code className="text-cyan-400">.cmd</code> shortcut in the Windows Startup directory or native Tauri autostart plugin.
          </p>

          <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/80 p-3.5 font-mono">
            <div>
              <span className="text-xs font-bold text-slate-200">Start with Windows</span>
              <p className="text-[10px] text-slate-500 mt-0.5">Launches backend daemon silently in background</p>
            </div>
            <button
              type="button"
              onClick={onStartupToggle}
              className={`rounded-full px-4 py-1.5 text-xs font-mono font-bold transition ${
                startupEnabled
                  ? "bg-emerald-950 text-emerald-300 border border-emerald-700/60"
                  : "bg-slate-800 text-slate-400 border border-slate-700"
              }`}
            >
              {startupEnabled ? "ENABLED" : "DISABLED"}
            </button>
          </div>

          <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/80 p-3.5 font-mono">
            <div>
              <span className="text-xs font-bold text-slate-200">Computer Control Master Switch</span>
              <p className="text-[10px] text-slate-500 mt-0.5">Hardware input & window automation</p>
            </div>
            <button
              type="button"
              onClick={onComputerToggle}
              className={`rounded-full px-4 py-1.5 text-xs font-mono font-bold transition ${
                computerEnabled
                  ? "bg-cyan-950 text-cyan-300 border border-cyan-700/60"
                  : "bg-rose-950 text-rose-300 border border-rose-700/60"
              }`}
            >
              {computerEnabled ? "ACTIVE" : "STOPPED"}
            </button>
          </div>
        </div>

        {/* AI Provider Hierarchy */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
            <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
              AI Provider Failover Sequence
            </span>
            <Cpu size={16} className="text-cyan-400" />
          </div>

          <p className="text-xs font-mono text-slate-300 leading-relaxed">
            Requests are dispatched through <code className="text-cyan-400">AIProviderRouter</code> with instant fallback on timeout or rate-limits:
          </p>

          <div className="space-y-2 font-mono text-xs">
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-2.5">
              <span className="text-cyan-200">1. Google Gemini</span>
              <span className="text-[10px] text-slate-500">gemini-3.8-flash</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-2.5">
              <span className="text-cyan-200">2. OpenRouter</span>
              <span className="text-[10px] text-slate-500">gpt-4o-mini / deepseek</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-2.5">
              <span className="text-cyan-200">3. NVIDIA NIM</span>
              <span className="text-[10px] text-slate-500">deepseek-v4.1-flash</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-2.5">
              <span className="text-cyan-200">4. Mock / Offline Engine</span>
              <span className="text-[10px] text-emerald-400">Deterministic Fallback</span>
            </div>
          </div>
        </div>
      </div>

      {/* Autonomy Level Slider */}
      <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4 font-mono">
        <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
          <div className="flex items-center gap-2 text-cyan-300 text-xs font-bold uppercase tracking-wider">
            <Sliders size={16} />
            <span>Agent Autonomy Governance Policy</span>
          </div>
          <span className="rounded bg-cyan-950 px-2 py-0.5 text-xs text-cyan-300 border border-cyan-800/40">
            LEVEL {autonomyLevel}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {autonomyLevels.map((item) => (
            <div
              key={item.level}
              onClick={() => item.level <= 1 && setAutonomyLevel(item.level)}
              className={`flex flex-col justify-between rounded-xl border p-3 text-xs transition ${
                autonomyLevel === item.level
                  ? "border-cyan-400 bg-cyan-950/40 text-cyan-100 shadow-[0_0_15px_rgba(6,182,212,0.2)]"
                  : item.level > 1
                  ? "border-slate-800/50 bg-slate-950/30 text-slate-600 opacity-60 cursor-not-allowed"
                  : "border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 cursor-pointer"
              }`}
            >
              <div>
                <span className="font-bold block mb-1 text-cyan-300">{item.title}</span>
                <p className="text-[10px] text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
              {autonomyLevel === item.level && (
                <div className="flex items-center gap-1 mt-3 text-[10px] text-emerald-400">
                  <CheckCircle2 size={12} />
                  <span>Selected</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
