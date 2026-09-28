import { useEffect, useRef, useState } from "react";
import { ChatPanel } from "./components/ChatPanel";
import { CommandInput } from "./components/CommandInput";
import { Header } from "./components/Header";
import { FloatingLauncher } from "./components/FloatingLauncher";
import { StatusIndicator } from "./components/StatusIndicator";
import { SystemStatus } from "./components/SystemStatus";
import { getComputerStatus, getHealth, sendChat, setComputerControl, setStartup } from "./lib/api";

export function App() {
  const [messages, setMessages] = useState<string[]>([]);
  const [online, setOnline] = useState(false);
  const [busy, setBusy] = useState(false);
  const [computerEnabled, setComputerEnabled] = useState(true);
  const [startupEnabled, setStartupEnabled] = useState(true);
  const [activated, setActivated] = useState(false);
  const commandRef = useRef<HTMLInputElement>(null);

  const activateD = () => {
    setActivated(true);
    commandRef.current?.focus();
  };

  useEffect(() => {
    getHealth()
      .then(() => setOnline(true))
      .catch(() => setOnline(false));
    getComputerStatus()
      .then((status) => {
        setComputerEnabled(status.computer_control);
        setStartupEnabled(status.startup_enabled);
      })
      .catch(() => undefined);
  }, []);

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col p-4 sm:p-8">
      <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-cyan-900/60 bg-slate-900/70 shadow-2xl shadow-cyan-950/30">
        <Header />
        <div className="flex flex-1 flex-col lg:flex-row">
          <div className="flex min-h-[32rem] flex-1 flex-col">
            <div className="flex items-center justify-between border-b border-cyan-950 px-6 py-3 text-xs uppercase tracking-widest text-slate-500">
              <span>Conversation</span>
              <StatusIndicator online={online} />
            </div>
            <ChatPanel messages={messages} />
            <CommandInput
              busy={busy}
              inputRef={commandRef}
              onSend={(value) => {
                setBusy(true);
                setMessages((current) => [...current, `USER  ${value}`]);
                sendChat(value)
                  .then((response) => {
                    const tool = response.tool_results[0];
                    const toolStatus = tool ? `TOOL  ${tool.tool}  ${tool.success ? "completed" : tool.error_code}` : "";
                    setMessages((current) => [...current, toolStatus, `D  ${response.message}`].filter(Boolean));
                  })
                  .catch(() => setMessages((current) => [...current, "D  Backend unavailable."]))
                  .finally(() => setBusy(false));
              }}
            />
          </div>
          <SystemStatus
            computerEnabled={computerEnabled}
            startupEnabled={startupEnabled}
            onComputerToggle={() => {
              const next = !computerEnabled;
              setComputerControl(next).then(() => setComputerEnabled(next)).catch(() => undefined);
            }}
            onStartupToggle={() => {
              const next = !startupEnabled;
              setStartup(next).then(() => setStartupEnabled(next)).catch(() => undefined);
            }}
          />
        </div>
      </div>
      <FloatingLauncher active={activated} onActivate={activateD} />
    </main>
  );
}
