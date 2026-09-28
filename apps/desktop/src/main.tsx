import { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { ChatPanel } from "./components/ChatPanel";
import { CommandInput } from "./components/CommandInput";
import { Header } from "./components/Header";
import { StatusIndicator } from "./components/StatusIndicator";
import { SystemStatus } from "./components/SystemStatus";
import { getHealth } from "./lib/api";
import "./styles.css";

function App() { const [messages, setMessages] = useState<string[]>([]); const [online, setOnline] = useState(false); useEffect(() => { getHealth().then(() => setOnline(true)).catch(() => setOnline(false)); }, []); return <main className="mx-auto flex min-h-screen max-w-6xl flex-col p-4 sm:p-8"><div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-cyan-900/60 bg-slate-900/70 shadow-2xl shadow-cyan-950/30"><Header /><div className="flex flex-1 flex-col lg:flex-row"><div className="flex min-h-[32rem] flex-1 flex-col"><div className="flex items-center justify-between border-b border-cyan-950 px-6 py-3 text-xs uppercase tracking-widest text-slate-500"><span>Conversation</span><StatusIndicator online={online} /></div><ChatPanel messages={messages} /><CommandInput onSend={(value) => setMessages((current) => [...current, `USER  ${value}`])} /></div><SystemStatus /></div></div></main>; }

createRoot(document.getElementById("root")!).render(<App />);
