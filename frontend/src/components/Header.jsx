export default function Header({ tab, onTabChange, savedCount, apiStatus }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="brand">
          <span className="brand-mark">JB</span>
          <div>
            <h1>JobBoard India</h1>
            <p className="brand-tag">Student job portal · All India</p>
          </div>
        </div>
        <nav className="header-nav">
          <button
            className={tab === "browse" ? "nav-active" : ""}
            onClick={() => onTabChange("browse")}
          >
            Browse jobs
          </button>
          <button
            className={tab === "saved" ? "nav-active" : ""}
            onClick={() => onTabChange("saved")}
          >
            Saved {savedCount > 0 && <span className="count-badge">{savedCount}</span>}
          </button>
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
