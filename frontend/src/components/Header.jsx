import { Link, useLocation } from "react-router-dom";

export default function Header({ tab, onTabChange, savedCount, apiStatus, variant = "browse" }) {
  const location = useLocation();
  const onDashboard = variant === "dashboard" || location.pathname === "/dashboard";

  return (
    <header className="header">
      <div className="header-inner">
        <Link to="/" className="brand brand-link">
          <span className="brand-mark">JB</span>
          <div>
            <h1>JobBoard India</h1>
            <p className="brand-tag">
              {onDashboard ? "Ops dashboard · Job health" : "Student job portal · All India"}
            </p>
          </div>
        </Link>

        <nav className="header-nav">
          {!onDashboard && (
            <>
              <button
                className={tab === "browse" ? "nav-active" : ""}
                onClick={() => onTabChange("browse")}
              >
                Browse jobs
              </button>
              <button
                className={tab === "others" ? "nav-active" : ""}
                onClick={() => onTabChange("others")}
              >
                Others
              </button>
              <button
                className={tab === "saved" ? "nav-active" : ""}
                onClick={() => onTabChange("saved")}
              >
                Saved {savedCount > 0 && <span className="count-badge">{savedCount}</span>}
              </button>
            </>
          )}
          <Link
            to="/dashboard"
            className={`header-link ${location.pathname === "/dashboard" ? "nav-active" : ""}`}
          >
            Ops dashboard
          </Link>
          <Link
            to="/dashboard/tag"
            className={`header-link ${location.pathname === "/dashboard/tag" ? "nav-active" : ""}`}
          >
            Tag jobs
          </Link>
          {onDashboard && (
            <Link to="/" className="header-link">
              ← Browse jobs
            </Link>
          )}
        </nav>

        <div className={`api-status ${apiStatus}`}>
          {apiStatus === "ok" && "API connected"}
          {apiStatus === "error" && "API offline"}
          {apiStatus === "loading" && "Connecting…"}
        </div>
      </div>
    </header>
  );
}
