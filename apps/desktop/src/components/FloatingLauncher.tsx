import { Sparkles } from "lucide-react";

export function FloatingLauncher({ active, onActivate }: { active: boolean; onActivate: () => void }) {
  return (
    <button
      type="button"
      aria-label={active ? "D is active" : "Activate D"}
      title={active ? "D is active" : "Activate D"}
      onClick={onActivate}
      className={`floating-launcher ${active ? "floating-launcher-active" : ""}`}
    >
      <span className="floating-launcher-mark">D</span>
      <span className="floating-launcher-label">{active ? "ACTIVE" : "ACTIVATE"}</span>
      <Sparkles size={15} aria-hidden="true" />
    </button>
  );
}
