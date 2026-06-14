import React, { useState } from 'react';
import logo from './assets/logo.jpg';

// Hardcoded credentials — replace with a proper auth backend for production
const VALID_USERS = [
  { username: 'admin',        password: 'psychocrowd2025' },
  { username: 'psychocrowd', password: 'admin123'         },
];

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [showPwd, setShowPwd]   = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    // Simulate slight delay for premium feel
    await new Promise(r => setTimeout(r, 800));

    const match = VALID_USERS.find(
      u => u.username === username.trim() && u.password === password
    );

    if (match) {
      sessionStorage.setItem('pc_auth', JSON.stringify({ user: username, ts: Date.now() }));
      onLogin(username);
    } else {
      setError('Identifiant ou mot de passe incorrect.');
    }
    setLoading(false);
  };

  return (
    <div className="login-page">
      {/* Animated background particles */}
      <div className="login-bg">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className={`particle particle-${i}`} />
        ))}
      </div>

      <div className="login-card">
        {/* Logo */}
        <div className="login-logo-wrap">
          <img src={logo} alt="PsychoCrowd Logo" className="login-logo" />
        </div>

        <div className="login-divider" />

        <h2 className="login-title">Accès Sécurisé</h2>
        <p className="login-subtitle">Connectez-vous pour accéder à la plateforme</p>

        <form onSubmit={handleSubmit} className="login-form">
          {/* Username */}
          <div className="login-field">
            <label htmlFor="login-username">
              <span className="field-icon">👤</span> Identifiant
            </label>
            <input
              id="login-username"
              type="text"
              autoComplete="username"
              placeholder="Entrez votre identifiant"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              className="login-input"
            />
          </div>

          {/* Password */}
          <div className="login-field">
            <label htmlFor="login-password">
              <span className="field-icon">🔒</span> Mot de passe
            </label>
            <div className="pwd-wrap">
              <input
                id="login-password"
                type={showPwd ? 'text' : 'password'}
                autoComplete="current-password"
                placeholder="Entrez votre mot de passe"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="login-input"
              />
              <button
                type="button"
                className="pwd-toggle"
                onClick={() => setShowPwd(v => !v)}
                aria-label={showPwd ? 'Masquer' : 'Afficher'}
              >
                {showPwd ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="login-error">
              <span>⚠️</span> {error}
            </div>
          )}

          {/* Submit */}
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? (
              <span className="login-spinner" />
            ) : (
              <>🚀 Connexion</>
            )}
          </button>
        </form>

        <p className="login-footer">
          PsychoCrowd © 2025 — AI Psychometric Engine
        </p>
      </div>
    </div>
  );
}
