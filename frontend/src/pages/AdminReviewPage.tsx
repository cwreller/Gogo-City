import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSubmissions, reviewSubmission, Submission } from '../api/submissions';
import { useAuth } from '../context/AuthContext';
import { ChevronLeft, Check, X, Loader2, MapPin, Clock, DollarSign, Tag } from 'lucide-react';

type TabStatus = 'pending' | 'approved' | 'rejected' | 'all';

export default function AdminReviewPage() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState<TabStatus>('pending');
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [reviewingId, setReviewingId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [xpValue, setXpValue] = useState('50');
  const [showRejectInput, setShowRejectInput] = useState<string | null>(null);

  useEffect(() => {
    if (!isAdmin) {
      navigate('/');
      return;
    }
    loadSubmissions();
  }, [tab, isAdmin]);

  const loadSubmissions = async () => {
    setLoading(true);
    try {
      const data = await getSubmissions(tab);
      setSubmissions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    setReviewingId(id);
    try {
      const updated = await reviewSubmission(id, 'approve', { xp: parseInt(xpValue) || 50 });
      setSubmissions((prev) => prev.map((s) => (s.id === id ? updated : s)));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to approve');
    } finally {
      setReviewingId(null);
    }
  };

  const handleReject = async (id: string) => {
    setReviewingId(id);
    try {
      const updated = await reviewSubmission(id, 'reject', { rejection_reason: rejectReason || undefined });
      setSubmissions((prev) => prev.map((s) => (s.id === id ? updated : s)));
      setShowRejectInput(null);
      setRejectReason('');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reject');
    } finally {
      setReviewingId(null);
    }
  };

  const TABS: { value: TabStatus; label: string }[] = [
    { value: 'pending', label: 'Pending' },
    { value: 'approved', label: 'Approved' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'all', label: 'All' },
  ];

  return (
    <div className="px-5 pt-8 pb-24 page-enter">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-[10px] text-[var(--color-text-muted)] mb-4 uppercase tracking-widest">
        <ChevronLeft size={14} /> Back
      </button>

      <h1 className="text-sm mb-1 uppercase tracking-widest">Admin Review</h1>
      <p className="font-sans text-xs text-[var(--color-text-muted)] mb-4">Review user-submitted task suggestions</p>

      <div className="flex gap-1 mb-5">
        {TABS.map((t) => (
          <button
            key={t.value}
            onClick={() => setTab(t.value)}
            className={`flex-1 py-2 text-[8px] uppercase tracking-widest border-2 transition-colors ${
              tab === t.value
                ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]'
                : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)]'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12">
          <Loader2 size={24} className="animate-spin mx-auto text-[var(--color-text-muted)]" />
        </div>
      ) : submissions.length === 0 ? (
        <div className="text-center py-12">
          <p className="font-sans text-xs text-[var(--color-text-muted)]">No {tab} submissions</p>
        </div>
      ) : (
        <div className="space-y-3">
          {submissions.map((sub) => {
            const isExpanded = expandedId === sub.id;
            const isPending = sub.status === 'pending';

            return (
              <div key={sub.id} className="card-retro overflow-hidden">
                <button
                  onClick={() => setExpandedId(isExpanded ? null : sub.id)}
                  className="w-full p-3 text-left"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-bold text-sm">{sub.name}</h3>
                      <p className="text-[10px] text-[var(--color-text-muted)] mt-0.5">
                        {sub.city_name} &middot; {sub.category} &middot; by @{sub.submitter_username}
                      </p>
                    </div>
                    <span className={`text-[8px] uppercase tracking-widest ml-2 shrink-0 ${
                      sub.status === 'approved' ? 'text-[var(--color-success)]' :
                      sub.status === 'rejected' ? 'text-[var(--color-error)]' :
                      'text-[var(--color-text-muted)]'
                    }`}>
                      {sub.status}
                    </span>
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-3 pb-3 border-t border-[var(--color-border)] pt-3 space-y-2">
                    {sub.description && (
                      <p className="font-sans text-xs text-[var(--color-text-muted)]">{sub.description}</p>
                    )}
                    {sub.task_description && (
                      <div>
                        <span className="text-[9px] text-[var(--color-text-muted)] uppercase tracking-widest">Task: </span>
                        <span className="font-sans text-xs">{sub.task_description}</span>
                      </div>
                    )}
                    <div className="flex flex-wrap gap-2 text-[9px] text-[var(--color-text-muted)]">
                      {sub.address && (
                        <span className="flex items-center gap-0.5"><MapPin size={10} /> {sub.address}</span>
                      )}
                      {sub.avg_duration_minutes && (
                        <span className="flex items-center gap-0.5"><Clock size={10} /> {sub.avg_duration_minutes}min</span>
                      )}
                      {sub.price_level && (
                        <span className="flex items-center gap-0.5"><DollarSign size={10} /> {'$'.repeat(sub.price_level)}</span>
                      )}
                      <span className="flex items-center gap-0.5"><Tag size={10} /> {sub.verification_type}</span>
                    </div>
                    {sub.vibe_tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {sub.vibe_tags.map((v) => (
                          <span key={v} className="px-2 py-0.5 text-[8px] bg-[var(--color-surface-light)] border border-[var(--color-border)] uppercase tracking-widest">
                            {v}
                          </span>
                        ))}
                      </div>
                    )}
                    {sub.verification_hint && (
                      <p className="font-sans text-[10px] text-[var(--color-text-muted)] italic">Hint: {sub.verification_hint}</p>
                    )}
                    {sub.pro_tips && (
                      <p className="font-sans text-[10px] text-[var(--color-text-muted)] italic">Tips: {sub.pro_tips}</p>
                    )}
                    {sub.rejection_reason && (
                      <p className="font-sans text-[10px] text-[var(--color-error)] bg-red-50 px-2 py-1 rounded">
                        Rejected: {sub.rejection_reason}
                      </p>
                    )}

                    {isPending && (
                      <div className="pt-2 space-y-2">
                        <div className="flex items-center gap-2">
                          <label className="text-[9px] text-[var(--color-text-muted)] uppercase tracking-widest shrink-0">XP:</label>
                          <input
                            type="number" value={xpValue} onChange={(e) => setXpValue(e.target.value)}
                            className="w-20 px-2 py-1 text-xs"
                            min={0}
                          />
                        </div>

                        {showRejectInput === sub.id ? (
                          <div className="space-y-2">
                            <input
                              value={rejectReason}
                              onChange={(e) => setRejectReason(e.target.value)}
                              placeholder="Reason for rejection (optional)"
                              className="w-full px-3 py-2 text-xs"
                            />
                            <div className="flex gap-2">
                              <button
                                onClick={() => { setShowRejectInput(null); setRejectReason(''); }}
                                className="flex-1 py-2 text-[9px] uppercase tracking-widest bg-white border-2 border-[var(--color-border)] btn-retro"
                              >
                                Cancel
                              </button>
                              <button
                                onClick={() => handleReject(sub.id)}
                                disabled={reviewingId === sub.id}
                                className="flex-1 py-2 text-[9px] uppercase tracking-widest bg-[var(--color-error)] text-white border-2 border-[var(--color-error)] btn-retro disabled:opacity-50 flex items-center justify-center gap-1"
                              >
                                {reviewingId === sub.id ? <Loader2 size={12} className="animate-spin" /> : <X size={12} />}
                                Confirm Reject
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="flex gap-2">
                            <button
                              onClick={() => setShowRejectInput(sub.id)}
                              className="flex-1 py-2 text-[9px] uppercase tracking-widest bg-white text-[var(--color-error)] border-2 border-[var(--color-error)] btn-retro flex items-center justify-center gap-1"
                            >
                              <X size={12} /> Reject
                            </button>
                            <button
                              onClick={() => handleApprove(sub.id)}
                              disabled={reviewingId === sub.id}
                              className="flex-1 py-2 text-[9px] uppercase tracking-widest bg-[var(--color-success)] text-white border-2 border-[var(--color-success)] btn-retro disabled:opacity-50 flex items-center justify-center gap-1"
                            >
                              {reviewingId === sub.id ? <Loader2 size={12} className="animate-spin" /> : <Check size={12} />}
                              Approve
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
