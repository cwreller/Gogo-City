import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { previewSharedRoute, importSharedRoute, SharedRoutePreview } from '../api/sharing';
import { ArrowLeft, MapPin, Clock, Tag, Download } from 'lucide-react';

export default function ImportPage() {
  const { shareCode } = useParams<{ shareCode: string }>();
  const [preview, setPreview] = useState<SharedRoutePreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!shareCode) return;
    previewSharedRoute(shareCode)
      .then(setPreview)
      .catch(() => setError('Route not found or invalid share code.'))
      .finally(() => setLoading(false));
  }, [shareCode]);

  const handleImport = async () => {
    if (!shareCode) return;
    setImporting(true);
    try {
      const instance = await importSharedRoute(shareCode);
      navigate(`/route/${instance.id}`);
    } catch {
      setError('Failed to import route. Please try again.');
      setImporting(false);
    }
  };

  if (loading) {
    return (
      <div className="px-4 pt-6 text-center text-xs text-[var(--color-text-muted)] uppercase tracking-widest">
        Loading preview...
      </div>
    );
  }

  if (error || !preview) {
    return (
      <div className="px-4 pt-6 pb-24">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] mb-3 hover:text-[var(--color-text)] uppercase tracking-widest"
        >
          <ArrowLeft size={14} /> Back
        </button>
        <div className="card-retro p-6 text-center">
          <p className="text-xs text-[var(--color-error)] uppercase tracking-widest">
            {error || 'Route not found'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 pt-6 pb-24">
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] mb-3 hover:text-[var(--color-text)] uppercase tracking-widest"
      >
        <ArrowLeft size={14} /> Back
      </button>

      <p className="text-[9px] text-[var(--color-primary)] uppercase tracking-widest mb-1">
        Shared Route
      </p>
      <h1 className="text-sm font-bold">{preview.title}</h1>
      {preview.description && (
        <p className="font-sans text-xs text-[var(--color-text-muted)] mt-1">{preview.description}</p>
      )}

      <div className="flex flex-wrap gap-2 mt-3">
        {preview.estimated_duration_minutes && (
          <span className="flex items-center gap-1 text-[9px] px-2 py-1 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-muted)] uppercase">
            <Clock size={10} />
            {Math.round(preview.estimated_duration_minutes / 60)}h
          </span>
        )}
        {preview.vibe_tags.map((tag) => (
          <span
            key={tag}
            className="flex items-center gap-1 text-[9px] px-2 py-1 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-muted)] uppercase"
          >
            <Tag size={10} />
            {tag}
          </span>
        ))}
      </div>

      <div className="card-retro p-4 mt-4 mb-4">
        <span className="text-[10px] uppercase tracking-widest text-[var(--color-text-muted)]">
          {preview.tasks.length} Tasks
        </span>
      </div>

      <div className="space-y-2">
        {preview.tasks.map((task) => (
          <div key={task.id} className="card-retro p-3 border-l-4 border-[var(--color-primary)]">
            <div className="flex items-start gap-3">
              <MapPin size={14} className="text-[var(--color-text-muted)] mt-0.5 shrink-0" />
              <div>
                <h3 className="font-bold text-xs">{task.name}</h3>
                {task.task_description && (
                  <p className="font-sans text-[10px] text-[var(--color-text-muted)] mt-0.5">{task.task_description}</p>
                )}
                {task.address && (
                  <p className="font-sans text-[10px] text-[var(--color-text-muted)] mt-0.5 italic">{task.address}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={handleImport}
        disabled={importing}
        className="w-full mt-6 py-4 bg-[var(--color-primary)] text-white text-sm uppercase tracking-widest btn-retro flex items-center justify-center gap-2 disabled:opacity-50"
      >
        <Download size={20} />
        {importing ? 'Importing...' : 'Import to My Routes'}
      </button>
    </div>
  );
}
