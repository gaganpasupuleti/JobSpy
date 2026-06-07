import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoggedIn, loading } = useAuth();
  const [email, setEmail] = useState("student@jobboard.test");
  const [password, setPassword] = useState("Student123!");
  const [error, setError] = useState(null);
  const [testAccounts, setTestAccounts] = useState([]);

  useEffect(() => {
    if (isLoggedIn) navigate("/", { replace: true });
  }, [isLoggedIn, navigate]);

  useEffect(() => {
    api
      .getTestAccounts()
      .then(setTestAccounts)
      .catch(() => {});
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    try {
      await login(email.trim(), password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  function useAccount(account) {
    setEmail(account.email);
    setPassword(account.password);
  }

  return (
    <div className="app login-page">
      <main className="login-card">
        <Link to="/" className="login-back">
          ← Back to job board
        </Link>
        <h1>Sign in</h1>
        <p className="login-sub">
          Use a test account below — no Google sign-in required.
        </p>

        {error && <div className="alert error">{error}</div>}

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          <button type="submit" className="btn primary lg" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        {testAccounts.length > 0 && (
          <section className="login-test-accounts">
            <h2>Test logins</h2>
            <p className="dash-muted">Click an account to fill the form.</p>
            <ul>
              {testAccounts.map((a) => (
                <li key={a.email}>
                  <button type="button" className="test-account-btn" onClick={() => useAccount(a)}>
                    <strong>{a.name}</strong>
                    <span>
                      {a.email} · password: <code>{a.password}</code>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        <p className="login-footnote">
          Ops tools still use the <Link to="/dashboard">admin API key</Link>, not these logins.
        </p>
      </main>
    </div>
  );
}
