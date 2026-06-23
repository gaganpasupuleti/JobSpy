import { cn } from "../../lib/utils";

export function Button({ className, variant = "default", size = "default", ...props }) {
  const variants = {
    default: "bg-navy text-white hover:bg-navy-dark",
    outline: "border border-slate-200 bg-white hover:bg-cream-dark text-navy",
    ghost: "hover:bg-cream-dark text-navy",
    destructive: "bg-red-600 text-white hover:bg-red-700",
  };
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-8 px-3 text-sm",
    lg: "h-11 px-6",
  };
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy/30 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    />
  );
}
