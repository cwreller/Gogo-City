import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { listInstances, InstanceListItem } from '../api/instances';
import { getLeaderboard } from '../api/checkins';
import { updateMe } from '../api/auth';
import XPBar from '../components/XPBar';
import { LogOut, Route, CheckCircle, MapPin, Pencil, PlusCircle, Shield, Database } from 'lucide-react';

export default function ProfilePage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [instances, setInstances] = useState<InstanceListItem[]>([]);
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [xp, setXP] = useState(0);
  const [level, setLevel] = useState(1);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState('');
  const [saving, setSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const startEditing = () => {
    setEditValue(displayName || username || '');
    setEditing(true);
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const saveDisplayName = async () => {
    const trimmed = editValue.trim();
    if (!trimmed || trimmed === displayName) {
      setEditing(false);
      return;
    }
    setSaving(true);
    try {
      const { access_token } = await updateMe(trimmed);
      auth.login(access_token);
      setDisplayName(trimmed);
    } catch (err) {
      console.error('Failed to update display name', err);
    } finally {
      setSaving(false);
      setEditing(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUsername(payload.username || '');
        setDisplayName(payload.display_name || '');
      } catch { /* ignore */ }
    }

    async function load() {
      try {
        const [inst, lb] = await Promise.all([listInstances(), getLeaderboard(100)]);
        setInstances(inst);
        if (token) {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const uid = payload.sub;
          const me = lb.find((e) => e.user_id === uid);
          if (me) {
            setXP(me.total_xp);
            setLevel(me.level);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleLogout = () => {
    auth.logout();
    navigate('/login');
  };

  const totalRoutes = instances.length;
  const completedRoutes = instances.filter((i) => i.status === 'completed').length;
  const totalTasks = instances.reduce((sum, i) => sum + i.progress.total_tasks, 0);
  const completedTasks = instances.reduce((sum, i) => sum + i.progress.completed_tasks, 0);

  if (loading) return <div className="px-4 pt-6 text-center text-xs text-[var(--color-text-muted)] uppercase tracking-widest">Loading...</div>;

  return (
    <div className="px-5 pt-8 pb-24 page-enter">
      <div className="flex justify-between items-start mb-6">
        <div>
          {editing ? (
            <input
              ref={inputRef}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onBlur={saveDisplayName}
              onKeyDown={(e) => { if (e.key === 'Enter') saveDisplayName(); if (e.key === 'Escape') setEditing(false); }}
              disabled={saving}
              maxLength={50}
              className="text-lg font-bold bg-transparent border-b-2 border-[var(--color-primary)] outline-none w-full"
            />
          ) : (
            <button onClick={startEditing} className="flex items-center gap-1.5 group">
              <h1 className="text-lg font-bold">{displayName || username || 'EXPLORER'}</h1>
              <Pencil size={14} className="text-[var(--color-text-muted)] opacity-0 group-hover:opacity-100 transition-opacity" />
            </button>
          )}
          {username && (
            <p className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest">@{username}</p>
          )}
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white border-2 border-[var(--color-border)] text-[9px] text-[var(--color-text-muted)] hover:text-[var(--color-error)] hover:border-[var(--color-error)] transition-colors uppercase tracking-widest"
        >
          <LogOut size={14} />
          Logout
        </button>
      </div>

      <XPBar xp={xp} level={level} />

      <div className="flex gap-2 mt-5 mb-3">
        <button
          onClick={() => navigate('/submit-task')}
          className="flex-1 py-3 bg-white text-xs uppercase tracking-widest btn-retro flex items-center justify-center gap-2"
        >
          <PlusCircle size={16} />
          Suggest Task
        </button>
        {auth.isAdmin && (
          <>
            <button
              onClick={() => navigate('/admin/submissions')}
              className="flex-1 py-3 bg-[var(--color-primary)] text-white text-xs uppercase tracking-widest btn-retro flex items-center justify-center gap-2"
            >
              <Shield size={16} />
              Review
            </button>
            <button
              onClick={() => navigate('/admin/tasks')}
              className="flex-1 py-3 bg-[var(--color-primary)] text-white text-xs uppercase tracking-widest btn-retro flex items-center justify-center gap-2"
            >
              <Database size={16} />
              Tasks DB
            </button>
          </>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="card-retro p-3 text-center">
          <Route size={20} className="mx-auto mb-1 text-[var(--color-primary)]" />
          <p className="text-sm font-bold">{totalRoutes}</p>
          <p className="text-[7px] text-[var(--color-text-muted)] uppercase tracking-widest">Quests</p>
        </div>
        <div className="card-retro p-3 text-center">
          <CheckCircle size={20} className="mx-auto mb-1 text-[var(--color-success)]" />
          <p className="text-sm font-bold">{completedRoutes}</p>
          <p className="text-[7px] text-[var(--color-text-muted)] uppercase tracking-widest">Cleared</p>
        </div>
        <div className="card-retro p-3 text-center">
          <MapPin size={20} className="mx-auto mb-1 text-[var(--color-primary)]" />
          <p className="text-sm font-bold">{completedTasks}/{totalTasks}</p>
          <p className="text-[7px] text-[var(--color-text-muted)] uppercase tracking-widest">Tasks</p>
        </div>
      </div>

      {instances.length > 0 && (
        <section className="mt-6">
          <h2 className="text-[10px] text-[var(--color-text-muted)] mb-3 uppercase tracking-widest">Quest History</h2>
          <div className="space-y-2">
            {instances.map((inst) => (
              <button
                key={inst.id}
                onClick={() => navigate(`/route/${inst.id}`)}
                className="w-full card-retro p-3 text-left hover:bg-[var(--color-surface-light)] transition-colors"
              >
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-sm">{inst.title}</h3>
                  <span className={`text-[8px] uppercase tracking-widest ${
                    inst.status === 'completed' ? 'text-[var(--color-success)]' : 'text-[var(--color-primary)]'
                  }`}>
                    {inst.status === 'completed' ? 'Done' : `${inst.progress.completed_tasks}/${inst.progress.total_tasks}`}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
