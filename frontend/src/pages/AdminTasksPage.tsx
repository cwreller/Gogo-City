import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { listCities, listCuratedTasks, City, CuratedTask } from '../api/cities';
import { ArrowLeft, MapPin, Camera, Shield, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const VERIFY_ICON = {
  gps: MapPin,
  photo: Camera,
  both: Shield,
};

export default function AdminTasksPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [cities, setCities] = useState<City[]>([]);
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [tasks, setTasks] = useState<CuratedTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    listCities().then(setCities);
  }, []);

  useEffect(() => {
    if (!selectedCity) { setTasks([]); return; }
    setLoading(true);
    listCuratedTasks(selectedCity)
      .then(setTasks)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedCity]);

  if (!auth.isAdmin) {
    return <div className="px-5 pt-8 text-center text-xs text-[var(--color-error)] uppercase tracking-widest">Admin access required</div>;
  }

  const categories = [...new Set(tasks.map((t) => t.category))].sort();

  return (
    <div className="px-5 pt-8 pb-24 page-enter">
      <button onClick={() => navigate('/profile')} className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] uppercase tracking-widest mb-4">
        <ArrowLeft size={14} /> Back
      </button>

      <h1 className="text-sm font-bold mb-1">Curated Tasks</h1>
      <p className="font-sans text-xs text-[var(--color-text-muted)] mb-4">View all curated tasks by city</p>

      <select
        value={selectedCity}
        onChange={(e) => setSelectedCity(e.target.value)}
        className="w-full px-4 py-3 text-sm border-2 border-[var(--color-border)] bg-white mb-4"
      >
        <option value="">Select a city...</option>
        {cities.map((c) => (
          <option key={c.id} value={c.id}>{c.name}{c.state ? `, ${c.state}` : ''}</option>
        ))}
      </select>

      {loading && <p className="text-center text-xs text-[var(--color-text-muted)] uppercase tracking-widest">Loading...</p>}

      {!loading && selectedCity && tasks.length === 0 && (
        <p className="text-center text-xs text-[var(--color-text-muted)] uppercase tracking-widest">No tasks for this city</p>
      )}

      {!loading && tasks.length > 0 && (
        <p className="text-[9px] text-[var(--color-text-muted)] uppercase tracking-widest mb-3">{tasks.length} tasks across {categories.length} categories</p>
      )}

      {categories.map((cat) => {
        const catTasks = tasks.filter((t) => t.category === cat);
        return (
          <div key={cat} className="mb-5">
            <h2 className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest mb-2">{cat} ({catTasks.length})</h2>
            <div className="space-y-2">
              {catTasks.map((task) => {
                const Icon = VERIFY_ICON[task.verification_type as keyof typeof VERIFY_ICON] || MapPin;
                const isExpanded = expandedId === task.id;
                return (
                  <div
                    key={task.id}
                    className={`card-retro p-3 border-l-4 ${task.is_active ? 'border-[var(--color-primary)]' : 'border-[var(--color-text-muted)] opacity-50'}`}
                  >
                    <div className="flex items-start gap-3 cursor-pointer" onClick={() => setExpandedId(isExpanded ? null : task.id)}>
                      <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-[var(--color-surface-light)] text-[var(--color-text-muted)] border border-[var(--color-border)]">
                        <Icon size={14} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-xs truncate">{task.name}</h3>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <span className="text-[8px] px-1.5 py-0.5 bg-[var(--color-surface-light)] text-[var(--color-text-muted)] border border-[var(--color-border)] uppercase">{task.verification_type}</span>
                          <span className="text-[8px] text-[var(--color-primary)]">{task.xp} XP</span>
                          {task.price_level && <span className="text-[8px] text-[var(--color-text-muted)]">{'$'.repeat(task.price_level)}</span>}
                          {task.avg_duration_minutes && <span className="text-[8px] text-[var(--color-text-muted)]">{task.avg_duration_minutes}min</span>}
                        </div>
                      </div>
                      <ChevronDown size={14} className={`text-[var(--color-text-muted)] shrink-0 mt-1 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                    </div>

                    {isExpanded && (
                      <div className="mt-3 pt-3 border-t border-[var(--color-border)] space-y-2 text-xs font-sans text-[var(--color-text-muted)]">
                        {task.task_description && <p><span className="font-bold text-[var(--color-text)]">Task:</span> {task.task_description}</p>}
                        {task.description && <p><span className="font-bold text-[var(--color-text)]">Description:</span> {task.description}</p>}
                        {task.address && <p><span className="font-bold text-[var(--color-text)]">Address:</span> {task.address}</p>}
                        {task.verification_hint && <p><span className="font-bold text-[var(--color-text)]">Hint:</span> {task.verification_hint}</p>}
                        {task.vibe_tags.length > 0 && (
                          <div className="flex gap-1 flex-wrap">
                            {task.vibe_tags.map((tag) => (
                              <span key={tag} className="text-[8px] px-1.5 py-0.5 bg-[var(--color-primary)] text-white uppercase">{tag}</span>
                            ))}
                          </div>
                        )}
                        {task.lat != null && task.lng != null && (
                          <p className="text-[8px]">📍 {Number(task.lat).toFixed(5)}, {Number(task.lng).toFixed(5)}</p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
