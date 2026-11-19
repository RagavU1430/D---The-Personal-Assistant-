import { useState } from "react";
import { GitBranch, GitCommit, GitPullRequest, Play, Copy, CheckCircle, XCircle, AlertCircle, RefreshCw, Terminal } from "lucide-react";

interface DeveloperJarvisPanelProps {
  busy: boolean;
  onCommand: (cmd: string) => void;
  latestResponse?: string;
}

interface TestResult {
  passed: number;
  failed: number;
  skipped: number;
  summary: string;
}

export function DeveloperJarvisPanel({ busy, onCommand, latestResponse }: DeveloperJarvisPanelProps) {
  const [output, setOutput] = useState<string>("");
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [copied, setCopied] = useState(false);
  const [activeAction, setActiveAction] = useState<string | null>(null);

  const dispatch = (label: string, cmd: string) => {
    setActiveAction(label);
    setOutput(`$ ${cmd}\n...`);
    onCommand(cmd);
  };

  // Parse latest response into terminal output
  const updateOutput = (resp: string) => {
    if (!resp) return;
    setOutput(resp);
    setActiveAction(null);

    // Try to detect test result pattern
    const passMatch = resp.match(/(\d+) passed/);
    const failMatch = resp.match(/(\d+) failed/);
    const skipMatch = resp.match(/(\d+) skipped/);
    if (passMatch || failMatch) {
      setTestResult({
        passed: passMatch ? parseInt(passMatch[1]) : 0,
        failed: failMatch ? parseInt(failMatch[1]) : 0,
        skipped: skipMatch ? parseInt(skipMatch[1]) : 0,
        summary: resp.split("\n")[0] ?? resp,
      });
    }
  };

  if (latestResponse && latestResponse !== output && !busy) {
    updateOutput(latestResponse);
  }

  const copyOutput = () => {
    navigator.clipboard.writeText(output).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  const gitActions = [
    { label: "Status", cmd: "git status", icon: <GitBranch size={14} /> },
    { label: "Diff", cmd: "git diff", icon: <GitPullRequest size={14} /> },
    { label: "Log", cmd: "git log", icon: <GitCommit size={14} /> },
    { label: "Branch", cmd: "git branch", icon: <GitBranch size={14} /> },
  ];

  return (
    <div className="flex flex-1 flex-col overflow-hidden p-4 gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal size={18} className="text-cyan-400" />
          <span className="text-sm font-bold tracking-widest text-cyan-200 font-mono uppercase">Developer JARVIS</span>
          <span className="text-[10px] font-mono text-slate-500 border border-slate-800 rounded px-1.5 py-0.5">Phase 5</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-500">
          <span className={`h-1.5 w-1.5 rounded-full ${busy ? "bg-amber-400 animate-pulse" : "bg-emerald-400"}`} />
          {busy ? "Executing..." : "Ready"}
        </div>
      </div>

      {/* Git Quick Actions */}
      <div className="flex flex-wrap gap-2">
        {gitActions.map((action) => (
          <button
            key={action.label}
            type="button"
            disabled={busy}
            onClick={() => dispatch(action.label, action.cmd)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-mono font-medium transition-all disabled:opacity-40 ${
              activeAction === action.label
                ? "border-cyan-400/60 bg-cyan-950/60 text-cyan-200 shadow-[0_0_10px_rgba(6,182,212,0.3)]"
                : "border-slate-800 bg-slate-900/60 text-slate-300 hover:border-cyan-800 hover:text-cyan-200"
            }`}
          >
            {action.icon}
            {action.label}
          </button>
        ))}

        {/* Divider */}
        <div className="h-7 w-px bg-slate-800 self-center" />

        {/* Run Tests */}
        <button
          type="button"
          disabled={busy}
          onClick={() => dispatch("Run Tests", "run tests")}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-mono font-medium transition-all disabled:opacity-40 ${
            activeAction === "Run Tests"
              ? "border-emerald-400/60 bg-emerald-950/60 text-emerald-200 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
              : "border-slate-800 bg-slate-900/60 text-slate-300 hover:border-emerald-800 hover:text-emerald-200"
          }`}
        >
          <Play size={13} />
          Run Tests
        </button>

        {/* Analyze Logs */}
        <button
          type="button"
          disabled={busy}
          onClick={() => dispatch("Analyze", "analyze logs")}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-xs font-mono font-medium text-slate-300 hover:border-amber-800 hover:text-amber-200 transition-all disabled:opacity-40"
        >
          <AlertCircle size={13} />
          Analyze Logs
        </button>

        <button
          type="button"
          disabled={busy}
          onClick={() => dispatch("Refresh", "git status")}
          className="ml-auto flex h-7 w-7 items-center justify-center rounded-lg border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-cyan-300 hover:border-cyan-800 transition disabled:opacity-40"
          title="Refresh git status"
        >
          <RefreshCw size={13} className={busy ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Test Result HUD */}
      {testResult && (
        <div className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-2 font-mono text-xs">
          <span className="text-slate-500 tracking-wider uppercase text-[10px]">Test Results</span>
          <div className="flex items-center gap-1.5 text-emerald-300">
            <CheckCircle size={13} />
            <span>{testResult.passed} passed</span>
          </div>
          <div className="flex items-center gap-1.5 text-rose-400">
            <XCircle size={13} />
            <span>{testResult.failed} failed</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span>⏭ {testResult.skipped} skipped</span>
          </div>
        </div>
      )}

      {/* Terminal Output Viewer */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-xl border border-cyan-950/80 bg-slate-950/90 shadow-inner">
        {/* Viewer header */}
        <div className="flex items-center justify-between border-b border-slate-900 px-4 py-2">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500/70" />
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500/70" />
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/70" />
            <span className="ml-3 text-[10px] font-mono text-slate-500 tracking-wider">TERMINAL OUTPUT</span>
          </div>
          <button
            type="button"
            onClick={copyOutput}
            disabled={!output}
            className="flex items-center gap-1 text-[10px] font-mono text-slate-500 hover:text-cyan-300 transition disabled:opacity-30"
          >
            <Copy size={11} />
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>

        {/* Output area */}
        <div className="flex-1 overflow-y-auto p-4">
          {output ? (
            <pre className="whitespace-pre-wrap text-xs font-mono text-cyan-100 leading-relaxed">
              {output}
            </pre>
          ) : (
            <div className="flex h-full items-center justify-center">
              <div className="text-center font-mono">
                <Terminal size={32} className="mx-auto mb-3 text-slate-700" />
                <p className="text-xs text-slate-600">Select a Git action or run tests above</p>
                <p className="text-[10px] text-slate-700 mt-1">Or type a command in the Assistant chat</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Security notice */}
      <div className="text-[10px] font-mono text-slate-600 text-center">
        All commands validated through TerminalService • Shell injection blocked • Working directory boundary enforced
      </div>
    </div>
  );
}
