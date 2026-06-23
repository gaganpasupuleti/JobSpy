import { useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "../../lib/utils";
import { Button } from "./Button";

export function Dialog({ open, onClose, title, children, className }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-navy/40" onClick={onClose} />
      <div
        className={cn(
          "relative z-10 w-full max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-xl",
          className
        )}
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <h2 className="text-lg font-semibold text-navy">{title}</h2>
          <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close">
            <X className="h-4 w-4" />
          </Button>
        </div>
        {children}
      </div>
    </div>
  );
}
