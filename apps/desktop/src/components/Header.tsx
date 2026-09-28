import { Activity } from "lucide-react";

export function Header() {
  return <header className="flex items-center justify-between border-b border-cyan-900/60 px-6 py-5"><div><p className="text-xl font-semibold tracking-[0.35em] text-cyan-200">D</p><p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">The Personal Assistant</p></div><div className="flex items-center gap-2 text-xs font-medium tracking-widest text-emerald-300"><Activity size={15} /> ONLINE</div></header>;
}
