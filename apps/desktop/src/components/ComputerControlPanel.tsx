import { useEffect, useState } from "react";
import {
  Monitor,
  Camera,
  Play,
  RotateCw,
  AppWindow,
  ShieldAlert,
  ShieldCheck,
  Code2,
  FolderOpen,
  Calculator,
  FileText,
  Globe,
  Compass,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import {
  executeTool,
  getActiveWindow,
  getWindows,
  setComputerControl,
  takeScreenshot,
} from "../lib/api";
import type { WindowInfo } from "../types/api";

interface ComputerControlPanelProps {
  computerControlActive: boolean;
  onToggleControl: () => void;
}

export function ComputerControlPanel({
  computerControlActive,
  onToggleControl,
}: ComputerControlPanelProps) {
  const [activeWindow, setActiveWindow] = useState<string>("Loading active window...");
  const [windows, setWindows] = useState<WindowInfo[]>([]);
  const [screenshotResult, setScreenshotResult] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const refreshState = async () => {
    setLoading(true);
    try {
      const active = await getActiveWindow();
      setActiveWindow(active.window?.title || "No active window detected");

      const list = await getWindows();
      setWindows(list.windows || []);
    } catch {
      setStatusMessage("Failed to poll Windows state");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshState();
    const interval = setInterval(refreshState, 8000);
    return () => clearInterval(interval);
  }, []);

  const launchApp = async (application: string) => {
    setStatusMessage(`Requesting launch of ${application}...`);
    try {
      const res = await executeTool("open_application", { application });
      if (res.success) {
        setStatusMessage(`Successfully launched ${application}`);
        setTimeout(refreshState, 1500);
      } else {
        setStatusMessage(`Failed to launch ${application}: ${res.message}`);
      }
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message}`);
    }
  };

  const captureDesktop = async () => {
    setStatusMessage("Capturing desktop screenshot...");
    try {
      const res = await takeScreenshot();
      if (res.success && res.data) {
        setScreenshotResult(res.data.temporary_path || "Captured temporary screenshot");
        setStatusMessage("Screenshot saved to temporary path.");
      } else {
        setStatusMessage(`Screenshot failed: ${res.message}`);
      }
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message}`);
    }
  };

  const allowlistedApps = [
    { name: "VS Code", id: "vscode", icon: <Code2 size={16} /> },
    { name: "File Explorer", id: "file_explorer", icon: <FolderOpen size={16} /> },
    { name: "Calculator", id: "calculator", icon: <Calculator size={16} /> },
    { name: "Notepad", id: "notepad", icon: <FileText size={16} /> },
    { name: "Google Chrome", id: "chrome", icon: <Globe size={16} /> },
    { name: "Microsoft Edge", id: "edge", icon: <Compass size={16} /> },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Emergency Stop / Status Banner */}
      <div
        className={`flex flex-wrap items-center justify-between gap-4 rounded-xl border p-4 backdrop-blur-md transition-all ${
          computerControlActive
            ? "border-emerald-500/40 bg-emerald-950/20 text-emerald-300"
            : "border-rose-500/50 bg-rose-950/40 text-rose-300 shadow-[0_0_20px_rgba(244,63,94,0.2)]"
        }`}
      >
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-lg border ${
              computerControlActive
                ? "border-emerald-500/50 bg-emerald-900/40 text-emerald-400"
                : "border-rose-500/50 bg-rose-900/60 text-rose-400"
            }`}
          >
            {computerControlActive ? <ShieldCheck size={20} /> : <ShieldAlert size={20} />}
          </div>
          <div>
            <h4 className="text-sm font-bold tracking-wider font-mono">
              COMPUTER CONTROL: {computerControlActive ? "ARMED & SAFE" : "EMERGENCY HALTED"}
            </h4>
            <p className="text-xs text-slate-400 font-mono">
              {computerControlActive
                ? "Actions are bounded by allowlists and confirmation checks."
                : "All desktop automation, mouse, keyboard, and launch actions are locked."}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={onToggleControl}
          className={`rounded-lg px-4 py-2 text-xs font-mono font-bold transition-all shadow-md ${
            computerControlActive
              ? "border border-rose-500/50 bg-rose-900/60 text-rose-200 hover:bg-rose-800"
              : "border border-emerald-500/50 bg-emerald-900/60 text-emerald-200 hover:bg-emerald-800"
          }`}
        >
          {computerControlActive ? "TRIGGER EMERGENCY STOP" : "RESUME AUTOMATION"}
        </button>
      </div>

      {statusMessage && (
        <div className="flex items-center gap-2 rounded-lg border border-cyan-800/60 bg-cyan-950/40 px-4 py-2.5 text-xs font-mono text-cyan-200">
          <AlertCircle size={14} className="text-cyan-400" />
          <span>{statusMessage}</span>
        </div>
      )}

      {/* Grid: Active Window & Screenshot */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Window Card */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
            <div className="flex items-center gap-2 text-cyan-300 font-mono text-xs font-bold uppercase tracking-wider">
              <Monitor size={16} />
              <span>Active Desktop Window</span>
            </div>
            <button
              type="button"
              onClick={refreshState}
              disabled={loading}
              className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-[11px] font-mono text-slate-300 hover:bg-slate-700 transition"
            >
              <RotateCw size={11} className={loading ? "animate-spin" : ""} />
              <span>Poll</span>
            </button>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-3.5 font-mono">
            <span className="text-[10px] uppercase tracking-wider text-slate-500">CURRENT FOCUS:</span>
            <p className="mt-1 text-sm font-semibold text-cyan-100 break-all">{activeWindow}</p>
          </div>

          <p className="text-[11px] text-slate-400 font-mono">
            Tracked via Windows Win32 <code className="text-cyan-400">GetForegroundWindow</code> with zero injected hooks.
          </p>
        </div>

        {/* Screenshot On-Demand */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
            <div className="flex items-center gap-2 text-cyan-300 font-mono text-xs font-bold uppercase tracking-wider">
              <Camera size={16} />
              <span>Screen Inspection</span>
            </div>
            <span className="rounded bg-cyan-950 px-2 py-0.5 text-[10px] font-mono text-cyan-400 border border-cyan-800/40">
              ON-DEMAND ONLY
            </span>
          </div>

          <p className="text-xs text-slate-300 font-mono leading-relaxed">
            Take a high-resolution, on-demand temporary snapshot of your desktop for multimodal inspection without continuous recording.
          </p>

          <button
            type="button"
            onClick={captureDesktop}
            disabled={!computerControlActive}
            className="flex items-center justify-center gap-2 w-full rounded-lg border border-cyan-500/40 bg-cyan-950/60 px-4 py-2.5 text-xs font-mono font-bold text-cyan-200 transition hover:bg-cyan-900/70 disabled:opacity-40"
          >
            <Camera size={15} />
            <span>CAPTURE DESKTOP SCREENSHOT</span>
          </button>

          {screenshotResult && (
            <div className="rounded bg-slate-950/90 p-2.5 text-[11px] font-mono text-emerald-300 flex items-center gap-2">
              <CheckCircle2 size={14} className="shrink-0" />
              <span className="truncate">Saved: {screenshotResult}</span>
            </div>
          )}
        </div>
      </div>

      {/* Allowlisted Applications Dock */}
      <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
        <div className="border-b border-cyan-950 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-cyan-300 font-mono text-xs font-bold uppercase tracking-wider">
              <Play size={15} />
              <span>Allowlisted Application Launcher</span>
            </div>
            <span className="text-[10px] font-mono text-slate-400">Pydantic Schema Guarded</span>
          </div>
          <p className="mt-1 text-xs text-slate-400 font-mono">
            Direct arbitrary shell commands are blocked. Only pre-configured, allowlisted binaries can be launched.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {allowlistedApps.map((app) => (
            <button
              key={app.id}
              type="button"
              onClick={() => launchApp(app.id)}
              disabled={!computerControlActive}
              className="flex flex-col items-center justify-center gap-2 rounded-xl border border-cyan-900/50 bg-slate-950/60 p-4 text-xs font-mono text-cyan-300 transition-all hover:border-cyan-400 hover:bg-cyan-950/40 hover:scale-105 active:scale-95 disabled:opacity-40"
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan-800/40 bg-cyan-950/50 text-cyan-400">
                {app.icon}
              </div>
              <span className="font-semibold text-center">{app.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Visible Windows Listing */}
      <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
        <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
          <div className="flex items-center gap-2 text-cyan-300 font-mono text-xs font-bold uppercase tracking-wider">
            <AppWindow size={16} />
            <span>Visible System Windows ({windows.length})</span>
          </div>
          <span className="text-[10px] font-mono text-slate-400">EnumWindows API</span>
        </div>

        <div className="max-h-60 overflow-y-auto space-y-2">
          {windows.length === 0 ? (
            <p className="text-xs font-mono text-slate-500 py-4 text-center">No open windows detected or query timed out.</p>
          ) : (
            windows.map((win, idx) => (
              <div
                key={`${win.title}-${idx}`}
                className="flex items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/60 px-3.5 py-2 text-xs font-mono text-slate-300"
              >
                <div className="flex items-center gap-2 truncate">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 shrink-0"></span>
                  <span className="truncate">{win.title}</span>
                </div>
                <span className="rounded bg-slate-900 px-2 py-0.5 text-[10px] text-slate-400 shrink-0">
                  {win.state || "VISIBLE"}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
