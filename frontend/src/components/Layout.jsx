import { NavLink } from "react-router-dom";
import { Bell, Briefcase, History, LayoutDashboard, Mail } from "lucide-react";
import { cn } from "../lib/utils";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/jobs", label: "Jobs", icon: Briefcase },
  { to: "/alerts", label: "Alerts", icon: Bell },
  { to: "/email-logs", label: "Email Logs", icon: Mail },
  { to: "/scan-runs", label: "Scan Runs", icon: History },
];

export function Layout({ children }) {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-xl font-bold text-navy">JobSpy Alerts Lab</h1>
            <p className="text-xs text-slate-500">Jobs + Email Alerts prototype</p>
          </div>
        </div>
      </header>
      <div className="mx-auto flex max-w-6xl gap-6 px-4 py-6">
        <nav className="hidden w-48 shrink-0 flex-col gap-1 md:flex">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-navy text-white"
                    : "text-slate-600 hover:bg-cream-dark hover:text-navy"
                )
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <main className="min-w-0 flex-1">{children}</main>
      </div>
      <nav className="fixed bottom-0 left-0 right-0 flex border-t border-slate-200 bg-white md:hidden">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex flex-1 flex-col items-center gap-1 py-2 text-[10px]",
                isActive ? "text-navy" : "text-slate-500"
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label.split(" ")[0]}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
