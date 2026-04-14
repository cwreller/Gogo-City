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
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-white">
      <img src="/logo.png" alt="GoGo City" className="w-40 mb-8" style={{ marginLeft: '1px' }} />

      <form onSubmit={handleSubmit} className="w-full space-y-4">
        <div>
          <label className="text-[10px] text-[var(--color-text-muted)] block mb-1 uppercase tracking-widest">Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-4 py-3 text-sm" />
        </div>
        <div>
          <label className="text-[10px] text-[var(--color-text-muted)] block mb-1 uppercase tracking-widest">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-4 py-3 text-sm" />
        </div>

        {error && <p className="text-[var(--color-error)] text-xs">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-[var(--color-primary)] text-white text-sm uppercase tracking-widest btn-retro disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'Sign In'}
        </button>
      </form>

      <div className="w-full flex items-center gap-3 my-5">
        <div className="flex-1 border-t border-[var(--color-border)]" />
        <span className="text-[9px] text-[var(--color-text-muted)] uppercase tracking-widest">or</span>
        <div className="flex-1 border-t border-[var(--color-border)]" />
      </div>

      <div ref={googleBtnRef} className="w-full" />

      <p className="mt-6 text-sm font-sans text-[var(--color-text-muted)]">
        New here?{' '}
        <Link to="/register" className="text-[var(--color-primary)] font-semibold hover:underline">
          Create account
        </Link>
      </p>
    </div>
  );
}
