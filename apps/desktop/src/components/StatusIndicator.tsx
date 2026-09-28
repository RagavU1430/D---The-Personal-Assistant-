export function StatusIndicator({ online }: { online: boolean }) { return <span className={online ? "text-emerald-300" : "text-amber-300"}>{online ? "● ONLINE" : "● OFFLINE"}</span>; }
