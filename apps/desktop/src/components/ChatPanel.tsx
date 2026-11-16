import { useRef, useEffect } from "react";
import { Bot, User, CheckCircle2, AlertTriangle, XCircle, Clock, Sparkles, Terminal } from "lucide-react";
import type { ChatMessageItem } from "../types/api";

interface ChatPanelProps {
  messages: ChatMessageItem[];
  onQuickPrompt?: (prompt: string) => void;
  busy?: boolean;
}

export function ChatPanel({ messages, onQuickPrompt, busy }: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  const quickPrompts = [
    { label: "Check System Status", prompt: "Check my system status" },
    { label: "Inspect Active Window", prompt: "What is my active window?" },
    { label: "Capture Screenshot", prompt: "Capture my screen" },
    { label: "Launch VS Code", prompt: "Open VS Code" },
    { label: "Check Memory Usage", prompt: "What is my RAM usage?" },
    { label: "Verify Health", prompt: "Check Jarvis health" },
  ];

  return (
    <section className="flex flex-1 flex-col overflow-hidden bg-slate-950/20">
      {/* Messages Stream */}
      <div className="flex-1 space-y-4 overflow-y-auto p-6 scroll-smooth">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-500/30 bg-cyan-950/20 text-cyan-400 shadow-[0_0_30px_rgba(6,182,212,0.15)]">
              <Bot size={32} />
            </div>
            <h3 className="mt-4 text-base font-bold tracking-wider text-cyan-200">
              D - OPERATING ASSISTANT READY
            </h3>
            <p className="mt-1.5 max-w-md text-xs text-slate-400 leading-relaxed font-mono">
              Always-on Windows assistant with safe tool execution, computer control, and calibrated failover reasoning.
            </p>

            {/* Quick Prompts */}
            <div className="mt-8 flex flex-wrap justify-center gap-2 max-w-xl">
              {quickPrompts.map((item) => (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => onQuickPrompt?.(item.prompt)}
                  className="flex items-center gap-1.5 rounded-lg border border-cyan-900/60 bg-slate-900/80 px-3 py-1.5 text-xs font-mono text-cyan-300 transition-all hover:border-cyan-500 hover:bg-cyan-950/50 hover:text-cyan-100 shadow-sm"
                >
                  <Sparkles size={12} className="text-cyan-400" />
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((item) => (
            <div
              key={item.id}
              className={`flex gap-3 text-sm ${
                item.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {item.sender !== "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-cyan-500/40 bg-cyan-950/60 text-cyan-300 shadow-sm">
                  <Bot size={16} />
                </div>
              )}

              <div
                className={`max-w-[85%] sm:max-w-xl rounded-xl border p-4 transition-all shadow-md ${
                  item.sender === "user"
                    ? "border-cyan-700/60 bg-gradient-to-br from-cyan-950/80 to-slate-900/90 text-cyan-50"
                    : "border-slate-800 bg-slate-900/90 text-slate-200"
                }`}
              >
                {/* Meta Header */}
                <div className="mb-2 flex items-center justify-between gap-4 text-[10px] font-mono uppercase tracking-wider text-slate-400">
                  <span className="font-semibold text-cyan-400">
                    {item.sender === "user" ? "USER" : "D - ASSISTANT"}
                  </span>
                  <div className="flex items-center gap-2">
                    {item.intent && (
                      <span className="rounded bg-cyan-950 px-1.5 py-0.5 text-[9px] text-cyan-300 border border-cyan-800/40">
                        {item.intent}
                      </span>
                    )}
                    <span>{item.timestamp}</span>
                  </div>
                </div>

                {/* Text Content */}
                <p className="whitespace-pre-wrap leading-relaxed font-sans text-sm">
                  {item.text}
                </p>

                {/* Plan Step Card (if generated) */}
                {item.plan && item.plan.steps.length > 0 && (
                  <div className="mt-3 rounded-lg border border-cyan-900/60 bg-slate-950/60 p-3 text-xs font-mono">
                    <div className="flex items-center gap-1.5 text-cyan-400 font-semibold mb-2">
                      <Terminal size={13} />
                      <span>EXECUTED PLAN: {item.plan.goal}</span>
                    </div>
                    <div className="space-y-1.5 text-[11px] text-slate-300">
                      {item.plan.steps.map((step) => (
                        <div key={step.id} className="flex items-start gap-2">
                          <span className="text-cyan-500 font-bold">↳</span>
                          <span>
                            [{step.action_type.toUpperCase()}] {step.tool ? `Tool: ${step.tool}` : step.description}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tool Execution Card (if present) */}
                {item.toolResult && (
                  <div className="mt-3 rounded-lg border border-cyan-900/70 bg-slate-950/80 p-3 text-xs font-mono">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="flex items-center gap-1.5 font-bold text-cyan-300">
                        {item.toolResult.success ? (
                          <CheckCircle2 size={14} className="text-emerald-400" />
                        ) : item.toolResult.error_code === "CONFIRMATION_REQUIRED" ? (
                          <AlertTriangle size={14} className="text-amber-400" />
                        ) : (
                          <XCircle size={14} className="text-rose-400" />
                        )}
                        <span>TOOL: {item.toolResult.tool}</span>
                      </div>
                      <div className="flex items-center gap-1 text-[10px] text-slate-400">
                        <Clock size={11} />
                        <span>{item.toolResult.execution_time_ms}ms</span>
                      </div>
                    </div>

                    <p className="mt-2 text-slate-300 text-[11px]">
                      {item.toolResult.message}
                    </p>

                    {item.toolResult.data && (
                      <div className="mt-2 rounded bg-slate-900/90 p-2 text-[10px] text-cyan-200/90 overflow-x-auto">
                        <pre>{JSON.stringify(item.toolResult.data, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {item.sender === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-cyan-700/60 bg-cyan-900/60 text-cyan-200 shadow-sm">
                  <User size={16} />
                </div>
              )}
            </div>
          ))
        )}

        {/* Busy Indicator */}
        {busy && (
          <div className="flex items-center gap-3 text-xs font-mono text-cyan-400 animate-pulse pl-2">
            <div className="h-2 w-2 rounded-full bg-cyan-400"></div>
            <span>D is reasoning and executing safe tools...</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </section>
  );
}
