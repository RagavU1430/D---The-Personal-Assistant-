import { Send } from "lucide-react";
import { RefObject, useState } from "react";

export function CommandInput({ onSend, busy, inputRef }: { onSend: (value: string) => void; busy?: boolean; inputRef?: RefObject<HTMLInputElement> }) {
	const [value, setValue] = useState("");
	const send = () => {
		if (value.trim() && !busy) {
			onSend(value.trim());
			setValue("");
		}
	};
	return <div className="flex gap-3 border-t border-cyan-950 p-4"><input ref={inputRef} aria-label="Command" disabled={busy} value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={(event) => event.key === "Enter" && send()} placeholder={busy ? "D is working..." : "Type a command..."} className="flex-1 rounded border border-cyan-900 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none focus:border-cyan-400 disabled:opacity-60" /><button onClick={send} disabled={busy} className="rounded bg-cyan-800 px-4 text-cyan-50 transition hover:bg-cyan-700 disabled:opacity-50" aria-label="Send command"><Send size={17} /></button></div>;
}
