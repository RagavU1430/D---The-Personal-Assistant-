import { useState } from "react";
import { FolderGit2, Trash2, ShieldCheck, AlertOctagon, CheckCircle2, FileQuestion } from "lucide-react";
import { executeTool } from "../lib/api";

export function FileIntelligencePanel() {
  const [filePath, setFilePath] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleRecycle = async () => {
    if (!filePath.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await executeTool("move_to_recycle_bin", { path: filePath.trim() });
      setResult(res);
    } catch (err: any) {
      setResult({
        success: false,
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Phase 4 Banner */}
      <div className="rounded-xl border border-cyan-800/60 bg-gradient-to-br from-slate-900/90 via-cyan-950/20 to-slate-900/90 p-5 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-cyan-500/40 bg-cyan-950/60 text-cyan-300">
            <FolderGit2 size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold tracking-wider text-cyan-100 font-mono">
                PHASE 4: FILE SYSTEM INTELLIGENCE
              </h3>
              <span className="rounded bg-cyan-950 px-2 py-0.5 text-[10px] font-mono text-cyan-300 border border-cyan-800/40">
                SAFE STORAGE ROOTS
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-400 font-mono leading-relaxed">
              Enables contextual document reading, project indexing, and safe reversible Recycle Bin management without arbitrary deletion.
            </p>
          </div>
        </div>
      </div>

      {/* Grid: Approved Roots & Safe Recycle */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Approved Roots */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
            <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
              Enforced File Boundaries
            </span>
            <ShieldCheck size={16} className="text-emerald-400" />
          </div>

          <p className="text-xs font-mono text-slate-300 leading-relaxed">
            All file reads and actions are strictly restricted to paths under <code className="text-cyan-400">APPROVED_FILE_ROOTS</code>. Paths attempting directory traversal (<code className="text-rose-400">..</code>) or targeting operating system drives are blocked by the permission engine before execution.
          </p>

          <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-3.5 font-mono text-xs">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1">APPROVED ROOT DIRECTORY:</span>
            <p className="text-cyan-200 break-all font-semibold">C:/Users/YourName/Desktop/Projects</p>
          </div>
        </div>

        {/* Reversible Recycle Bin Tool */}
        <div className="rounded-xl border border-cyan-900/60 bg-slate-900/70 p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
            <span className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider">
              Safe Reversible Deletion
            </span>
            <Trash2 size={16} className="text-amber-400" />
          </div>

          <p className="text-xs font-mono text-slate-300 leading-relaxed">
            Moves items to the native Windows Recycle Bin using <code className="text-cyan-400">SHFileOperationW</code> with <code className="text-cyan-400">FOF_ALLOWUNDO</code>. Permanent deletions are strictly prohibited.
          </p>

          <div className="space-y-2">
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="Full path to file within approved root..."
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 font-mono outline-none focus:border-cyan-400"
            />
            <button
              type="button"
              onClick={handleRecycle}
              disabled={loading || !filePath.trim()}
              className="flex items-center justify-center gap-2 w-full rounded-lg border border-amber-600/40 bg-amber-950/40 px-4 py-2.5 text-xs font-mono font-bold text-amber-200 hover:bg-amber-900/50 disabled:opacity-40 transition"
            >
              <Trash2 size={14} />
              <span>TEST RECYCLE BIN MOVE (CONFIRMATION REQUIRED)</span>
            </button>
          </div>

          {result && (
            <div className="rounded bg-slate-950/90 p-3 text-xs font-mono border border-slate-800">
              <div className="flex items-center gap-2 font-bold mb-1">
                {result.success ? (
                  <CheckCircle2 size={14} className="text-emerald-400" />
                ) : (
                  <AlertOctagon size={14} className="text-amber-400" />
                )}
                <span className={result.success ? "text-emerald-300" : "text-amber-300"}>
                  {result.error_code || (result.success ? "SUCCESS" : "ERROR")}
                </span>
              </div>
              <p className="text-[11px] text-slate-300">{result.message}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
