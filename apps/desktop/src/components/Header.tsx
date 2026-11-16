import { Activity, ShieldAlert, ShieldCheck, Terminal, Cpu, FolderGit2, Settings, MonitorPlay, Mic, Volume2 } from "lucide-react";

export type ViewTab = "chat" | "computer" | "tools" | "files" | "settings";

interface HeaderProps {
  currentTab: ViewTab;
  onTabChange: (tab: ViewTab) => void;
  online: boolean;
  computerControlActive: boolean;
  onToggleComputerControl: () => void;
  lifecycleState: string;
  onOpenVoiceAssistant: () => void;
}

export function Header({
  currentTab,
  onTabChange,
  online,
  computerControlActive,
  onToggleComputerControl,
  lifecycleState,
  onOpenVoiceAssistant,
}: HeaderProps) {
  const tabs: { id: ViewTab; label: string; icon: React.ReactNode }[] = [
    { id: "chat", label: "Assistant", icon: <Terminal size={15} /> },
    { id: "computer", label: "Desktop Control", icon: <MonitorPlay size={15} /> },
    { id: "tools", label: "Safe Tools", icon: <Cpu size={15} /> },
    { id: "files", label: "Files (Phase 4)", icon: <FolderGit2 size={15} /> },
    { id: "settings", label: "Settings", icon: <Settings size={15} /> },
  ];

  return (
    <header className="flex flex-col border-b border-cyan-900/60 bg-slate-950/70 backdrop-blur-md">
      {/* Top Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 px-6 py-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-lg border border-cyan-500/50 bg-cyan-950/60 shadow-[0_0_15px_rgba(6,182,212,0.25)]">
            <span className="text-xl font-bold tracking-widest text-cyan-200">D</span>
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${online ? "bg-cyan-400" : "bg-rose-400"}`}></span>
              <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${online ? "bg-cyan-500" : "bg-rose-500"}`}></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-[0.25em] text-cyan-100">D - ASSISTANT</span>
              <span className="rounded bg-cyan-950/80 px-2 py-0.5 text-[10px] font-mono tracking-wider text-cyan-400 border border-cyan-800/60">
                VOICE & COMPUTER READY
              </span>
            </div>
            <p className="text-[11px] font-mono tracking-wider text-slate-400">
              Personal AI Operating Assistant • Laptop & Desktop Optimized
            </p>
          </div>
        </div>

        {/* Global Controls & Status Indicators */}
        <div className="flex items-center gap-3">
          {/* Quick Voice Assistant Launcher Button */}
          <button
            type="button"
            onClick={onOpenVoiceAssistant}
            className="flex items-center gap-1.5 rounded-full border border-cyan-400/50 bg-gradient-to-r from-cyan-950 via-slate-900 to-cyan-950 px-3.5 py-1 text-xs font-mono font-bold text-cyan-200 hover:border-cyan-300 hover:scale-105 shadow-[0_0_15px_rgba(6,182,212,0.3)] transition"
          >
            <Mic size={14} className="text-cyan-400 animate-pulse" />
            <span>VOICE ASSIST</span>
          </button>

          {/* Runtime State */}
          <div className="hidden sm:flex items-center gap-1.5 rounded-full border border-slate-800 bg-slate-900/90 px-3 py-1 text-xs font-mono text-slate-300">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>
            <span className="text-[10px] tracking-wider uppercase text-slate-500">STATE:</span>
            <span className="font-semibold text-cyan-300">{lifecycleState || "READY"}</span>
          </div>

          {/* Computer Control Emergency Switch */}
          <button
            type="button"
            onClick={onToggleComputerControl}
            title={computerControlActive ? "Click to emergency stop computer control" : "Click to resume computer control"}
            className={`flex items-center gap-1.5 rounded-full px-3.5 py-1 text-xs font-mono font-medium transition-all ${
              computerControlActive
                ? "border border-emerald-500/40 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/50 shadow-[0_0_10px_rgba(16,185,129,0.15)]"
                : "border border-rose-500/50 bg-rose-950/60 text-rose-300 hover:bg-rose-900/60 shadow-[0_0_12px_rgba(244,63,94,0.3)] animate-pulse"
            }`}
          >
            {computerControlActive ? <ShieldCheck size={14} /> : <ShieldAlert size={14} />}
            <span>CONTROL: {computerControlActive ? "ACTIVE" : "STOPPED"}</span>
          </button>

          {/* Backend Status */}
          <div
            className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-mono font-medium ${
              online
                ? "border border-cyan-800/40 bg-cyan-950/30 text-cyan-300"
                : "border border-rose-800/40 bg-rose-950/30 text-rose-400"
            }`}
          >
            <Activity size={14} className={online ? "text-cyan-400 animate-pulse" : "text-rose-400"} />
            <span className="hidden sm:inline">{online ? "ONLINE" : "DISCONNECTED"}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-t border-cyan-950/80 bg-slate-950/40 px-6 overflow-x-auto no-scrollbar">
        {tabs.map((tab) => {
          const isActive = currentTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-xs font-mono font-medium transition-all whitespace-nowrap ${
                isActive
                  ? "border-cyan-400 text-cyan-200 bg-cyan-950/30 shadow-[inset_0_-2px_8px_rgba(6,182,212,0.2)]"
                  : "border-transparent text-slate-400 hover:border-slate-700 hover:text-slate-200"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
