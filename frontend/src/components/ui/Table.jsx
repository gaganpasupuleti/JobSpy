import { cn } from "../../lib/utils";

export function Table({ className, ...props }) {
  return (
    <div className="w-full overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className={cn("w-full text-sm", className)} {...props} />
    </div>
  );
}

export function THead({ className, ...props }) {
  return <thead className={cn("bg-cream-dark/60", className)} {...props} />;
}

export function TBody({ className, ...props }) {
  return <tbody className={cn("divide-y divide-slate-100", className)} {...props} />;
}

export function TR({ className, ...props }) {
  return <tr className={cn("hover:bg-cream/50", className)} {...props} />;
}

export function TH({ className, ...props }) {
  return (
    <th
      className={cn(
        "px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500",
        className
      )}
      {...props}
    />
  );
}

export function TD({ className, ...props }) {
  return <td className={cn("px-4 py-3 text-slate-700", className)} {...props} />;
}
