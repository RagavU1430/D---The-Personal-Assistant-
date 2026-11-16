import { useEffect, useState } from "react";
import { Mic, MicOff, Volume2, VolumeX, X, Sparkles, AlertCircle } from "lucide-react";
import { voiceEngine } from "../lib/voice";

interface VoiceAssistantOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  onVoiceCommand: (command: string) => void;
  isProcessing: boolean;
  assistantSpokenResponse?: string;
  voiceMuted: boolean;
  onToggleMute: () => void;
}

export function VoiceAssistantOverlay({
  isOpen,
  onClose,
  onVoiceCommand,
  isProcessing,
  assistantSpokenResponse,
  voiceMuted,
  onToggleMute,
}: VoiceAssistantOverlayProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Automatically speak assistant response when received and not muted
  useEffect(() => {
    if (assistantSpokenResponse && !voiceMuted && isOpen) {
      voiceEngine.speak(assistantSpokenResponse, {
        onStart: () => setIsSpeaking(true),
        onEnd: () => setIsSpeaking(false),
      });
    }
  }, [assistantSpokenResponse, voiceMuted, isOpen]);

  // Handle start/stop listening
  const handleToggleListening = () => {
    if (isListening) {
      voiceEngine.stopListening();
      setIsListening(false);
    } else {
      setErrorMessage(null);
      setTranscript("");
      const started = voiceEngine.startListening(
        (text, isFinal) => {
          setTranscript(text);
          if (isFinal && text.trim()) {
            setIsListening(false);
            onVoiceCommand(text.trim());
          }
        },
        (error) => {
          setErrorMessage(error);
          setIsListening(false);
        },
        () => {
          setIsListening(false);
        },
      );
      if (started) {
        setIsListening(true);
      }
    }
  };

  // Auto-start listening on open
  useEffect(() => {
    if (isOpen) {
      handleToggleListening();
    } else {
      voiceEngine.stopListening();
      voiceEngine.stopSpeaking();
      setIsListening(false);
      setIsSpeaking(false);
    }
    return () => {
      voiceEngine.stopListening();
      voiceEngine.stopSpeaking();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const quickVoicePrompts = [
    "Check system status",
    "What is my active window?",
    "Capture screenshot",
    "Open VS Code",
    "Check my RAM usage",
    "Find all python files",
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-xl p-4 transition-all">
      <div className="relative flex w-full max-w-2xl flex-col items-center rounded-3xl border border-cyan-500/40 bg-gradient-to-b from-slate-900/95 via-slate-950/95 to-slate-900/95 p-8 shadow-[0_0_80px_rgba(6,182,212,0.25)] text-center">
        {/* Top Header */}
        <div className="flex w-full items-center justify-between border-b border-cyan-950/80 pb-4 font-mono text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span className="font-bold tracking-widest text-cyan-300 uppercase">D • Voice Assist System</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onToggleMute}
              className="flex items-center gap-1 rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-slate-300 hover:text-cyan-200 transition"
            >
              {voiceMuted ? <VolumeX size={13} className="text-rose-400" /> : <Volume2 size={13} className="text-cyan-400" />}
              <span>{voiceMuted ? "MUTED" : "SPEECH ON"}</span>
            </button>

            <button
              type="button"
              onClick={onClose}
              className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-800 hover:bg-slate-800 hover:text-slate-200 transition"
              title="Close Voice Assistant"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Central Futuristic Voice Holographic Orb */}
        <div className="my-10 flex flex-col items-center justify-center">
          <div className="relative flex items-center justify-center">
            {/* Ambient Energy Rings */}
            <div
              className={`absolute h-48 w-48 rounded-full border border-cyan-500/20 transition-all duration-700 ${
                isListening || isSpeaking
                  ? "scale-125 animate-ping opacity-60 border-cyan-400"
                  : isProcessing
                  ? "animate-spin border-amber-400/40"
                  : "scale-100 opacity-20"
              }`}
            ></div>

            <div
              className={`absolute h-36 w-36 rounded-full border transition-all duration-500 ${
                isListening
                  ? "border-cyan-400/60 shadow-[0_0_40px_rgba(6,182,212,0.6)] animate-pulse"
                  : isSpeaking
                  ? "border-emerald-400/60 shadow-[0_0_40px_rgba(16,185,129,0.6)] animate-pulse"
                  : isProcessing
                  ? "border-amber-400/60 shadow-[0_0_40px_rgba(245,158,11,0.5)]"
                  : "border-slate-800"
              }`}
            ></div>

            {/* Main Interactive Mic Orb */}
            <button
              type="button"
              onClick={handleToggleListening}
              className={`relative z-10 flex h-28 w-28 items-center justify-center rounded-full border-2 transition-all duration-300 shadow-2xl ${
                isListening
                  ? "border-cyan-300 bg-gradient-to-tr from-cyan-600 via-cyan-500 to-cyan-300 text-slate-950 scale-110 shadow-[0_0_50px_rgba(6,182,212,0.8)]"
                  : isSpeaking
                  ? "border-emerald-300 bg-gradient-to-tr from-emerald-600 via-emerald-500 to-emerald-300 text-slate-950 scale-105 shadow-[0_0_50px_rgba(16,185,129,0.8)]"
                  : isProcessing
                  ? "border-amber-300 bg-gradient-to-tr from-amber-600 via-amber-500 to-amber-300 text-slate-950 scale-105"
                  : "border-cyan-800/80 bg-gradient-to-tr from-slate-900 to-cyan-950/80 text-cyan-300 hover:border-cyan-400 hover:scale-105"
              }`}
            >
              {isListening ? (
                <Mic size={38} className="animate-bounce" />
              ) : isSpeaking ? (
                <Volume2 size={38} className="animate-pulse" />
              ) : isProcessing ? (
                <Sparkles size={38} className="animate-spin" />
              ) : (
                <Mic size={36} />
              )}
            </button>
          </div>

          {/* Audio Waveform Bars */}
          <div className="mt-6 flex h-8 items-center justify-center gap-1.5">
            {[40, 75, 55, 95, 60, 85, 45, 90, 65, 50].map((h, i) => (
              <span
                key={i}
                className={`w-1 rounded-full transition-all duration-150 ${
                  isListening
                    ? "bg-cyan-400 animate-pulse"
                    : isSpeaking
                    ? "bg-emerald-400 animate-pulse"
                    : isProcessing
                    ? "bg-amber-400"
                    : "bg-slate-800"
                }`}
                style={{
                  height: isListening || isSpeaking ? `${Math.max(12, Math.round(h * Math.random()))}px` : "6px",
                  animationDelay: `${i * 70}ms`,
                }}
              ></span>
            ))}
          </div>

          {/* Status Label */}
          <p className="mt-3 text-xs font-mono font-bold tracking-widest uppercase text-cyan-200">
            {isListening
              ? "Listening to your voice..."
              : isProcessing
              ? "D is reasoning and executing tools..."
              : isSpeaking
              ? "D is responding aloud..."
              : "Tap Microphone to Speak"}
          </p>
        </div>

        {/* Live Transcript / Response Card */}
        <div className="w-full rounded-2xl border border-cyan-900/60 bg-slate-950/80 p-5 font-mono shadow-inner">
          <span className="text-[10px] uppercase tracking-wider text-slate-500 block mb-1">
            {transcript ? "DETECTED SPEECH:" : "TRANSCRIPT:"}
          </span>
          <p className="text-sm font-semibold text-cyan-100 min-h-[1.5rem] leading-relaxed">
            {transcript ? `"${transcript}"` : isProcessing ? "Processing command..." : "Say a command, e.g. 'Check my system status'"}
          </p>

          {errorMessage && (
            <div className="mt-3 flex items-center justify-center gap-2 text-xs text-rose-400">
              <AlertCircle size={14} />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        {/* Quick Voice Suggestions */}
        <div className="mt-6 w-full">
          <p className="text-[10px] font-mono tracking-wider text-slate-500 uppercase mb-2">
            Try Speaking These Commands:
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {quickVoicePrompts.map((cmd) => (
              <button
                key={cmd}
                type="button"
                onClick={() => {
                  setTranscript(cmd);
                  onVoiceCommand(cmd);
                }}
                className="rounded-lg border border-cyan-900/50 bg-slate-900/70 px-3 py-1.5 text-xs font-mono text-cyan-300 hover:border-cyan-500 hover:bg-cyan-950/50 transition shadow-sm"
              >
                "{cmd}"
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
