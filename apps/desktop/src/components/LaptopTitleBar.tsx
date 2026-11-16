import { Minus, Square, X, Laptop, Minimize2, Mic, Volume2, VolumeX } from "lucide-react";

interface LaptopTitleBarProps {
  isCompactMode: boolean;
  onToggleCompactMode: () => void;
  voiceActive: boolean;
  onToggleVoice: () => void;
  voiceMuted: boolean;
  onToggleMute: () => void;
}

export function LaptopTitleBar({
  isCompactMode,
  onToggleCompactMode,
  voiceActive,
  onToggleVoice,
  voiceMuted,
  onToggleMute,
}: LaptopTitleBarProps) {
  return (
    <div className="flex h-10 select-none items-center justify-between border-b border-cyan-950/80 bg-slate-950/90 px-4 text-xs font-mono backdrop-blur-md">
      {/* Left: Window Dots / Branding */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-full bg-rose-500/80 transition hover:bg-rose-400 cursor-pointer shadow-sm"></span>
          <span className="h-3 w-3 rounded-full bg-amber-500/80 transition hover:bg-amber-400 cursor-pointer shadow-sm"></span>
          <span className="h-3 w-3 rounded-full bg-emerald-500/80 transition hover:bg-emerald-400 cursor-pointer shadow-sm"></span>
        </div>

        <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-slate-800">
          <Laptop size={13} className="text-cyan-400" />
          <span className="font-bold tracking-wider text-cyan-200">D — PERSONAL ASSISTANT</span>
          <span className="text-[10px] text-slate-500">v0.1.0</span>
        </div>
      </div>

      {/* Center: Live Voice Pill */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onToggleVoice}
          className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-[11px] font-bold transition-all shadow-sm ${
            voiceActive
              ? "border border-cyan-400/60 bg-cyan-950/80 text-cyan-200 shadow-[0_0_12px_rgba(6,182,212,0.4)] animate-pulse"
              : "border border-slate-800 bg-slate-900/60 text-slate-400 hover:border-cyan-700/60 hover:text-cyan-300"
          }`}
        >
          <Mic size={13} className={voiceActive ? "text-cyan-300 animate-bounce" : "text-slate-400"} />
          <span>{voiceActive ? "VOICE ASSIST ACTIVE" : "START VOICE ASSIST"}</span>
        </button>

        <button
          type="button"
          onClick={onToggleMute}
          title={voiceMuted ? "Unmute spoken voice replies" : "Mute spoken voice replies"}
          className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-cyan-300 transition"
        >
          {voiceMuted ? <VolumeX size={13} className="text-rose-400" /> : <Volume2 size={13} className="text-cyan-400" />}
        </button>
      </div>

      {/* Right: Window Sizing Controls */}
      <div className="flex items-center gap-1 text-slate-400">
        <button
          type="button"
          onClick={onToggleCompactMode}
          title={isCompactMode ? "Expand to Full Laptop View" : "Collapse to Compact HUD Widget"}
          className="flex h-7 px-2 items-center gap-1.5 rounded hover:bg-slate-800/80 hover:text-cyan-200 transition text-[11px]"
        >
          <Minimize2 size={13} />
          <span className="hidden md:inline">{isCompactMode ? "EXPAND" : "HUD MODE"}</span>
        </button>

        <div className="flex items-center pl-1 border-l border-slate-800">
          <button
            type="button"
            className="flex h-7 w-7 items-center justify-center rounded hover:bg-slate-800 hover:text-slate-200 transition"
            title="Minimize window"
          >
            <Minus size={13} />
          </button>
          <button
            type="button"
            className="flex h-7 w-7 items-center justify-center rounded hover:bg-slate-800 hover:text-slate-200 transition"
            title="Maximize window"
          >
            <Square size={11} />
          </button>
          <button
            type="button"
            className="flex h-7 w-7 items-center justify-center rounded hover:bg-rose-950/80 hover:text-rose-300 transition"
            title="Close window"
          >
            <X size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}
