import { cn } from "../../lib/utils";
import { Info } from "lucide-react";

export function Alert({ className, variant = "info", children, ...props }) {
  const variants = {
    info: "border-blue-200 bg-blue-50 text-blue-900",
    warning: "border-amber-200 bg-amber-50 text-amber-900",
    success: "border-emerald-200 bg-emerald-50 text-emerald-900",
  };
  return (
    <div
      role="alert"
      className={cn(
        "flex gap-3 rounded-xl border p-4 text-sm",
        variants[variant],
        className
      )}
      {...props}
    >
      <Info className="mt-0.5 h-4 w-4 shrink-0" />
      <div>{children}</div>
    </div>
  );
}
