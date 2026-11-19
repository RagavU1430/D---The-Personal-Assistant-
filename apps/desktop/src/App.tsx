import { useEffect, useRef, useState } from "react";
import { Header, type ViewTab } from "./components/Header";
import { LaptopTitleBar } from "./components/LaptopTitleBar";
import { VoiceAssistantOverlay } from "./components/VoiceAssistantOverlay";
import { ChatPanel } from "./components/ChatPanel";
import { CommandInput } from "./components/CommandInput";
import { ComputerControlPanel } from "./components/ComputerControlPanel";
import { SafeToolsPanel } from "./components/SafeToolsPanel";
import { FileIntelligencePanel } from "./components/FileIntelligencePanel";
import { DeveloperJarvisPanel } from "./components/DeveloperJarvisPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { FloatingLauncher } from "./components/FloatingLauncher";
import { getComputerStatus, getHealth, sendChat, setComputerControl, setStartup } from "./lib/api";
import { voiceEngine } from "./lib/voice";
import type { ChatMessageItem } from "./types/api";

export function App() {
  const [currentTab, setCurrentTab] = useState<ViewTab>("chat");
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [online, setOnline] = useState<boolean>(false);
  const [busy, setBusy] = useState<boolean>(false);
  const [computerEnabled, setComputerEnabled] = useState<boolean>(true);
  const [startupEnabled, setStartupEnabled] = useState<boolean>(true);
  const [lifecycleState, setLifecycleState] = useState<string>("READY");
  const [activated, setActivated] = useState<boolean>(false);

  // Laptop Window & Voice Assist States
  const [isCompactMode, setIsCompactMode] = useState<boolean>(false);
  const [voiceOverlayOpen, setVoiceOverlayOpen] = useState<boolean>(false);
  const [voiceMuted, setVoiceMuted] = useState<boolean>(false);
  const [latestVoiceResponse, setLatestVoiceResponse] = useState<string>("");

  const commandRef = useRef<HTMLInputElement>(null);

  const activateD = () => {
    setActivated(true);
    setCurrentTab("chat");
    setTimeout(() => {
      commandRef.current?.focus();
    }, 100);
  };

  const pollStatus = () => {
    getHealth()
      .then(() => setOnline(true))
      .catch(() => setOnline(false));

    getComputerStatus()
      .then((status) => {
        setComputerEnabled(status.computer_control);
        setStartupEnabled(status.startup_enabled);
        setLifecycleState(status.status);
      })
      .catch(() => undefined);
  };

  useEffect(() => {
    pollStatus();
    const interval = setInterval(pollStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = (value: string) => {
    if (!value.trim() || busy) return;
    setBusy(true);

    const userMessage: ChatMessageItem = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: value,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);

    sendChat(value)
      .then((response) => {
        const assistantMessage: ChatMessageItem = {
          id: `assistant-${Date.now()}`,
          sender: "assistant",
          text: response.message,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
          intent: response.intent,
          toolResult: response.tool_results?.[0],
          plan: response.plan,
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setLatestVoiceResponse(response.message);

        // Read aloud if not muted and voice is enabled
        if (!voiceMuted) {
          voiceEngine.speak(response.message);
        }
      })
      .catch(() => {
        const errorMessage: ChatMessageItem = {
          id: `err-${Date.now()}`,
          sender: "system",
          text: "D backend is currently unavailable. Please verify the backend service is running on port 8001.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
        };
        setMessages((prev) => [...prev, errorMessage]);
      })
      .finally(() => {
        setBusy(false);
      });
  };

  const handleToggleComputer = () => {
    const next = !computerEnabled;
    setComputerControl(next)
      .then(() => setComputerEnabled(next))
      .catch(() => undefined);
  };

  const handleToggleStartup = () => {
    const next = !startupEnabled;
    setStartup(next)
      .then(() => setStartupEnabled(next))
      .catch(() => undefined);
  };

  return (
    <main
      className={`mx-auto flex min-h-screen flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200 transition-all duration-300 ${
        isCompactMode
          ? "max-w-xl p-2 sm:p-4 justify-center"
          : "max-w-7xl p-3 sm:p-6 lg:p-8"
      }`}
    >
      <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-cyan-800/60 bg-slate-950/85 shadow-[0_0_60px_rgba(4,20,38,0.85)] backdrop-blur-2xl">
        {/* Native Laptop TitleBar */}
        <LaptopTitleBar
          isCompactMode={isCompactMode}
          onToggleCompactMode={() => setIsCompactMode((prev) => !prev)}
          voiceActive={voiceOverlayOpen}
          onToggleVoice={() => setVoiceOverlayOpen((prev) => !prev)}
          voiceMuted={voiceMuted}
          onToggleMute={() => {
            setVoiceMuted((prev) => {
              const next = !prev;
              if (next) voiceEngine.stopSpeaking();
              return next;
            });
          }}
        />

        {/* Main Application Header */}
        <Header
          currentTab={currentTab}
          onTabChange={setCurrentTab}
          online={online}
          computerControlActive={computerEnabled}
          onToggleComputerControl={handleToggleComputer}
          lifecycleState={lifecycleState}
          onOpenVoiceAssistant={() => setVoiceOverlayOpen(true)}
        />

        {/* Tab Views */}
        <div className="flex flex-1 overflow-hidden">
          {currentTab === "chat" && (
            <div className="flex flex-1 flex-col overflow-hidden">
              <ChatPanel
                messages={messages}
                onQuickPrompt={(prompt) => handleSendMessage(prompt)}
                busy={busy}
              />
              <CommandInput
                busy={busy}
                inputRef={commandRef}
                onSend={handleSendMessage}
                onOpenVoiceAssistant={() => setVoiceOverlayOpen(true)}
              />
            </div>
          )}

          {currentTab === "computer" && (
            <ComputerControlPanel
              computerControlActive={computerEnabled}
              onToggleControl={handleToggleComputer}
            />
          )}

          {currentTab === "tools" && <SafeToolsPanel />}

          {currentTab === "files" && <FileIntelligencePanel />}

          {currentTab === "developer" && (
            <DeveloperJarvisPanel
              busy={busy}
              onCommand={handleSendMessage}
              latestResponse={latestVoiceResponse}
            />
          )}

          {currentTab === "settings" && (
            <SettingsPanel
              computerEnabled={computerEnabled}
              startupEnabled={startupEnabled}
              onComputerToggle={handleToggleComputer}
              onStartupToggle={handleToggleStartup}
            />
          )}
        </div>
      </div>

      {/* Futuristic Voice Assistant Holographic Overlay */}
      <VoiceAssistantOverlay
        isOpen={voiceOverlayOpen}
        onClose={() => setVoiceOverlayOpen(false)}
        onVoiceCommand={(cmd) => {
          handleSendMessage(cmd);
        }}
        isProcessing={busy}
        assistantSpokenResponse={latestVoiceResponse}
        voiceMuted={voiceMuted}
        onToggleMute={() => {
          setVoiceMuted((prev) => {
            const next = !prev;
            if (next) voiceEngine.stopSpeaking();
            return next;
          });
        }}
      />

      <FloatingLauncher active={activated} onActivate={activateD} />
    </main>
  );
}
