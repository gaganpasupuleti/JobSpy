import { cn } from "../../lib/utils";

export function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        "flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy/20",
        className
      )}
      {...props}
    />
  );
}

export function Textarea({ className, ...props }) {
  return (
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy/20",
        className
      )}
      {...props}
    />
  );
}

export function Select({ className, children, ...props }) {
  return (
    <select
      className={cn(
        "flex h-10 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy/20",
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
}

export function Label({ className, ...props }) {
  return (
    <label
      className={cn("text-sm font-medium text-slate-700", className)}
      {...props}
    />
  );
}

export function Checkbox({ className, ...props }) {
  return (
    <input
      type="checkbox"
      className={cn(
        "h-4 w-4 rounded border-slate-300 text-navy focus:ring-navy/30",
        className
      )}
      {...props}
    />
  );
}
