import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listInstances, deleteInstance, updateInstanceStatus, InstanceListItem } from '../api/instances';
import { getLeaderboard } from '../api/checkins';
import XPBar from '../components/XPBar';
import { Compass, ChevronRight, Zap, Archive, Trash2, X } from 'lucide-react';

const LONG_PRESS_MS = 500;

export default function HomePage() {
  const [instances, setInstances] = useState<InstanceListItem[]>([]);
  const [userXP, setUserXP] = useState(0);
  const [userLevel, setUserLevel] = useState(1);
  const [loading, setLoading] = useState(true);
  const [actionTarget, setActionTarget] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const longPressTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    try {
      const [inst, lb] = await Promise.all([listInstances(), getLeaderboard(100)]);
      setInstances(inst);
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const uid = payload.sub;
          const me = lb.find((e) => e.user_id === uid);
          if (me) {
            setUserXP(me.total_xp);
            setUserLevel(me.level);
          }
        } catch { /* ignore */ }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleArchive = async (id: string) => {
    try {
      await updateInstanceStatus(id, 'archived');
      setActionTarget(null);
      load();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteInstance(id);
      setConfirmDelete(null);
      setActionTarget(null);
      load();
    } catch (err) {
      console.error(err);
    }
  };

  const startLongPress = (id: string) => {
    longPressTimer.current = setTimeout(() => {
      setActionTarget(id);
    }, LONG_PRESS_MS);
  };

  const cancelLongPress = () => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }
  };

  const handleCardClick = (id: string) => {
    if (actionTarget) return;
    navigate(`/route/${id}`);
  };

  const active = instances.filter((i) => i.status === 'active');
  const completed = instances.filter((i) => i.status === 'completed');

  const renderCard = (inst: InstanceListItem, variant: 'active' | 'completed') => {
    const isTarget = actionTarget === inst.id;
    const pct = inst.progress.percent;

    return (
      <div key={inst.id} className="relative">
        <button
          onClick={() => handleCardClick(inst.id)}
          onMouseDown={() => startLongPress(inst.id)}
          onMouseUp={cancelLongPress}
          onMouseLeave={cancelLongPress}
          onTouchStart={() => startLongPress(inst.id)}
          onTouchEnd={cancelLongPress}
          onTouchCancel={cancelLongPress}
          onContextMenu={(e) => { e.preventDefault(); setActionTarget(inst.id); }}
          className={`w-full card-retro ${variant === 'active' ? 'p-4' : 'p-3.5'} text-left transition-all select-none group`}
        >
          <div className="flex justify-between items-start">
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-sm font-sans truncate">{inst.title}</h3>
              {variant === 'active' && (
                <p className="text-[10px] text-[var(--color-text-muted)] font-sans mt-0.5">
                  {inst.progress.completed_tasks} of {inst.progress.total_tasks} tasks
                </p>
              )}
            </div>
            {variant === 'active' ? (
              <ChevronRight size={18} className="text-[var(--color-text-muted)] group-hover:text-[var(--color-primary)] group-hover:translate-x-0.5 transition-all shrink-0 mt-0.5" />
            ) : (
              <span className="text-[9px] text-white bg-[var(--color-success)] px-2 py-0.5 rounded-full font-sans font-medium uppercase shrink-0">
                Done
              </span>
            )}
          </div>
          {variant === 'active' && (
            <div className="mt-3 flex items-center gap-3">
              <div className="flex-1 progress-retro h-2.5">
                <div className="progress-retro-fill h-full" style={{ width: `${pct}%` }} />
              </div>
              <span className="text-[10px] font-sans font-semibold text-[var(--color-primary)] tabular-nums min-w-[32px] text-right">
                {Math.round(pct)}%
              </span>
            </div>
          )}
        </button>

        {isTarget && (
          <div className="absolute right-0 top-0 h-full flex items-center gap-1.5 pr-3 z-10">
            <button
              onClick={() => setConfirmDelete(inst.id)}
              className="p-2.5 bg-[var(--color-error)] text-white rounded-xl shadow-lg"
              title="Delete"
            >
              <Trash2 size={14} />
            </button>
            {inst.status === 'active' && (
              <button
                onClick={() => handleArchive(inst.id)}
                className="p-2.5 bg-gray-500 text-white rounded-xl shadow-lg"
                title="Archive"
              >
                <Archive size={14} />
              </button>
            )}
            <button
              onClick={() => setActionTarget(null)}
              className="p-2.5 bg-white border border-[var(--color-border)] rounded-xl shadow-lg"
              title="Cancel"
            >
              <X size={14} />
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="pb-28 page-enter">
      <div className="hero-banner px-5 pt-8 pb-6 mb-5">
        <h1 className="text-3xl mb-1 tracking-tight" style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800 }}>
          <span className="bg-gradient-to-r from-[#e8832a] to-[#e55a2f] bg-clip-text text-transparent">GoGo</span>
          <span className="text-[#2d2d2d]">City</span>
        </h1>
        <p className="text-[9px] text-[var(--color-text-muted)] mb-5 uppercase tracking-[0.25em] font-sans">
          Explore. Complete. Level up.
        </p>

        <XPBar xp={userXP} level={userLevel} />
      </div>

      <div className="px-5">
        <button
          onClick={() => navigate('/generate')}
          className="w-full py-4 text-white text-sm uppercase tracking-widest rounded-xl font-sans font-semibold bg-gradient-to-r from-[#e8832a] to-[#e55a2f] shadow-lg shadow-orange-500/20 hover:shadow-orange-500/30 transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-2"
        >
          <Compass size={20} />
          New Quest
        </button>
      </div>

      <div className="px-5">
      {loading ? (
        <div className="mt-8 text-center text-xs text-[var(--color-text-muted)] uppercase tracking-widest font-sans animate-pulse">Loading...</div>
      ) : (
        <>
          {active.length > 0 && (
            <section className="mt-6">
              <h2 className="text-[10px] mb-3 uppercase tracking-[0.2em] text-[var(--color-primary)] font-sans font-semibold flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)] animate-pulse" />
                Active Quests
              </h2>
              <div className="space-y-3">
                {active.map((inst) => renderCard(inst, 'active'))}
              </div>
            </section>
          )}

          {completed.length > 0 && (
            <section className="mt-7">
              <h2 className="text-[10px] mb-3 uppercase tracking-[0.2em] text-[var(--color-success)] font-sans font-semibold flex items-center gap-2">
                <Zap size={12} />
                Completed
              </h2>
              <div className="space-y-2">
                {completed.map((inst) => renderCard(inst, 'completed'))}
              </div>
            </section>
          )}

          {instances.length === 0 && (
            <div className="mt-14 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center">
                <Compass size={28} className="text-[var(--color-primary)] opacity-60" />
              </div>
              <p className="text-sm font-sans font-semibold text-[var(--color-text)] mb-1">No quests yet</p>
              <p className="font-sans text-xs text-[var(--color-text-muted)]">
                Tap <span className="text-[var(--color-primary)] font-medium">New Quest</span> to start exploring!
              </p>
            </div>
          )}
        </>
      )}
      </div>

      {confirmDelete && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-end justify-center">
          <div className="w-full max-w-[430px] bg-white rounded-t-3xl p-6 pb-8 shadow-2xl">
            <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-5" />
            <h3 className="text-base font-bold font-sans mb-2">Delete Quest?</h3>
            <p className="font-sans text-sm text-[var(--color-text-muted)] mb-6 leading-relaxed">
              This will permanently remove the quest and all progress. This cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmDelete(null)}
                className="flex-1 py-3.5 text-xs uppercase tracking-widest border border-[var(--color-border)] bg-white rounded-xl font-sans font-semibold active:scale-[0.98] transition-transform"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(confirmDelete)}
                className="flex-1 py-3.5 text-xs uppercase tracking-widest bg-[var(--color-error)] text-white rounded-xl font-sans font-semibold shadow-lg shadow-red-500/20 active:scale-[0.98] transition-transform"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
