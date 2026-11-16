import { Send, CornerDownLeft, Mic } from "lucide-react";
import { RefObject, useState } from "react";

interface CommandInputProps {
  onSend: (value: string) => void;
  busy?: boolean;
  inputRef?: RefObject<HTMLInputElement>;
  onOpenVoiceAssistant?: () => void;
}

export function CommandInput({ onSend, busy, inputRef, onOpenVoiceAssistant }: CommandInputProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    if (value.trim() && !busy) {
      onSend(value.trim());
      setValue("");
    }
  };

  return (
    <div className="border-t border-cyan-950/80 bg-slate-950/80 p-4 backdrop-blur-md">
      <div className="flex items-center gap-3">
        {onOpenVoiceAssistant && (
          <button
            type="button"
            onClick={onOpenVoiceAssistant}
            title="Talk to D with Voice Assist"
            className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-500/40 bg-cyan-950/70 text-cyan-300 hover:bg-cyan-900/80 hover:scale-105 active:scale-95 shadow-[0_0_12px_rgba(6,182,212,0.25)] transition"
          >
            <Mic size={18} className="animate-pulse" />
          </button>
        )}

        <div className="relative flex-1">
          <input
            ref={inputRef}
            aria-label="Command"
            disabled={busy}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder={busy ? "D is executing..." : "Instruct D (or speak via microphone button)..."}
            className="w-full rounded-xl border border-cyan-900/60 bg-slate-900/90 px-4 py-3 text-sm text-cyan-50 placeholder-slate-500 outline-none transition-all focus:border-cyan-400 focus:ring-2 focus:ring-cyan-500/20 disabled:opacity-50 font-sans"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:flex items-center gap-1 text-[10px] font-mono text-slate-500">
            <span>ENTER</span>
            <CornerDownLeft size={10} />
          </div>
        </div>

        <button
          type="button"
          onClick={handleSend}
          disabled={busy || !value.trim()}
          className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-500/40 bg-gradient-to-br from-cyan-600 to-cyan-800 text-white shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all hover:from-cyan-500 hover:to-cyan-700 hover:scale-105 active:scale-95 disabled:opacity-40 disabled:hover:scale-100"
          aria-label="Send command"
        >
          <Send size={16} />
        </button>
      </div>

      <div className="mt-2 flex items-center justify-between px-1 text-[10px] font-mono text-slate-500">
        <span>Restricted environment • All commands validated through ToolExecutor</span>
        <span>Voice Assist: ENABLED</span>
      </div>
    </div>
  );
}
