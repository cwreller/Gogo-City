import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login, googleLogin } from '../api/auth';

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void;
          renderButton: (element: HTMLElement, config: Record<string, unknown>) => void;
        };
      };
    };
  }
}

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const auth = useAuth();
  const navigate = useNavigate();
  const googleBtnRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    if (!clientId || !window.google) return;

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: async (response: { credential: string }) => {
        setError('');
        setLoading(true);
        try {
          const { access_token } = await googleLogin(response.credential);
          auth.login(access_token);
          navigate('/');
        } catch (err: any) {
          setError(err.response?.data?.detail || 'Google sign-in failed');
        } finally {
          setLoading(false);
        }
      },
    });

    if (googleBtnRef.current) {
      window.google.accounts.id.renderButton(googleBtnRef.current, {
        theme: 'outline',
        size: 'large',
        width: googleBtnRef.current.offsetWidth,
        text: 'signin_with',
      });
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { access_token } = await login(email, password);
      auth.login(access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 login-bg relative overflow-hidden">
      <div className="login-blob login-blob-1" />
      <div className="login-blob login-blob-2" />

      <div className="relative z-10 w-full max-w-sm">
        <div className="text-center mb-8">
          <img src="/logo.png" alt="GoGo City" className="w-40 mx-auto mb-3" />
          <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-[0.25em] font-sans">
            Explore. Complete. Level up.
          </p>
        </div>

        <div className="login-card rounded-2xl p-6 space-y-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-1.5 uppercase tracking-widest font-sans font-medium">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 text-sm font-sans rounded-lg"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-1.5 uppercase tracking-widest font-sans font-medium">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 text-sm font-sans rounded-lg"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 text-[var(--color-error)] text-xs font-sans bg-red-50 px-3 py-2 rounded-lg border border-red-100">
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-gradient-to-r from-[#e8832a] to-[#e55a2f] text-white text-sm uppercase tracking-widest font-sans font-semibold rounded-xl shadow-lg shadow-orange-500/20 hover:shadow-orange-500/30 transition-all duration-200 active:scale-[0.98] disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="flex items-center gap-3">
            <div className="flex-1 border-t border-[var(--color-border)]" />
            <span className="text-[9px] text-[var(--color-text-muted)] uppercase tracking-widest font-sans">or</span>
            <div className="flex-1 border-t border-[var(--color-border)]" />
          </div>

          <div ref={googleBtnRef} className="w-full" />
        </div>

        <p className="mt-6 text-center text-sm font-sans text-[var(--color-text-muted)]">
          New here?{' '}
          <Link to="/register" className="text-[var(--color-primary)] font-semibold hover:underline">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
}
