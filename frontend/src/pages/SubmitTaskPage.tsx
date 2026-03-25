import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listCities, City } from '../api/cities';
import { submitTask, getMySubmissions, Submission } from '../api/submissions';
import { Send, ChevronLeft, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const CATEGORY_OPTIONS = [
  'food', 'bars', 'cafes', 'music', 'museums', 'nature',
  'photo-spots', 'active', 'shopping', 'street-art', 'nightlife', 'history',
];

const VIBE_OPTIONS = [
  'foodie', 'cultural', 'nightlife', 'adventurous', 'chill',
  'photography', 'music', 'outdoors', 'social', 'history', 'romantic',
];

const VERIFICATION_TYPES = ['photo', 'gps', 'both'] as const;

export default function SubmitTaskPage() {
  const navigate = useNavigate();
  const [cities, setCities] = useState<City[]>([]);
  const [mySubmissions, setMySubmissions] = useState<Submission[]>([]);
  const [showForm, setShowForm] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const [cityId, setCityId] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [address, setAddress] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [verificationHint, setVerificationHint] = useState('');
  const [verificationType, setVerificationType] = useState<string>('photo');
  const [category, setCategory] = useState('');
  const [vibes, setVibes] = useState<string[]>([]);
  const [priceLevel, setPriceLevel] = useState<number | null>(null);
  const [duration, setDuration] = useState('');
  const [proTips, setProTips] = useState('');

  useEffect(() => {
    listCities().then((c) => {
      setCities(c);
      if (c.length > 0) setCityId(c[0].id);
    });
    getMySubmissions().then(setMySubmissions).catch(() => {});
  }, []);

  const toggleVibe = (v: string) =>
    setVibes((prev) => prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]);

  const resetForm = () => {
    setName('');
    setDescription('');
    setAddress('');
    setTaskDescription('');
    setVerificationHint('');
    setVerificationType('photo');
    setCategory('');
    setVibes([]);
    setPriceLevel(null);
    setDuration('');
    setProTips('');
    setSuccess(false);
  };

  const handleSubmit = async () => {
    if (!name.trim() || !category || !cityId) return;
    setSubmitting(true);
    try {
      const result = await submitTask({
        city_id: cityId,
        name: name.trim(),
        description: description.trim() || undefined,
        address: address.trim() || undefined,
        task_description: taskDescription.trim() || undefined,
        verification_hint: verificationHint.trim() || undefined,
        verification_type: verificationType,
        category,
        vibe_tags: vibes,
        price_level: priceLevel,
        avg_duration_minutes: duration ? parseInt(duration) : null,
        pro_tips: proTips.trim() || undefined,
      });
      setMySubmissions((prev) => [result, ...prev]);
      setSuccess(true);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  const statusIcon = (s: string) => {
    if (s === 'approved') return <CheckCircle size={14} className="text-[var(--color-success)]" />;
    if (s === 'rejected') return <XCircle size={14} className="text-[var(--color-error)]" />;
    return <Clock size={14} className="text-[var(--color-text-muted)]" />;
  };

  if (success) {
    return (
      <div className="px-5 pt-8 pb-24 page-enter text-center">
        <CheckCircle size={48} className="mx-auto mb-4 text-[var(--color-success)]" />
        <h1 className="text-sm uppercase tracking-widest mb-2">Submitted!</h1>
        <p className="font-sans text-xs text-[var(--color-text-muted)] mb-6">
          Your task suggestion is pending admin review. You'll see it in your submissions once approved.
        </p>
        <div className="flex gap-3 justify-center">
          <button onClick={resetForm} className="px-6 py-3 bg-white text-xs uppercase tracking-widest btn-retro">
            Submit Another
          </button>
          <button onClick={() => navigate('/profile')} className="px-6 py-3 bg-[var(--color-primary)] text-white text-xs uppercase tracking-widest btn-retro">
            Back to Profile
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="px-5 pt-8 pb-24 page-enter">
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-[10px] text-[var(--color-text-muted)] mb-4 uppercase tracking-widest">
        <ChevronLeft size={14} /> Back
      </button>

      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setShowForm(true)}
          className={`flex-1 py-2 text-[9px] uppercase tracking-widest border-2 transition-colors ${
            showForm ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]' : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)]'
          }`}
        >
          New Suggestion
        </button>
        <button
          onClick={() => setShowForm(false)}
          className={`flex-1 py-2 text-[9px] uppercase tracking-widest border-2 transition-colors ${
            !showForm ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]' : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)]'
          }`}
        >
          My Submissions ({mySubmissions.length})
        </button>
      </div>

      {showForm ? (
        <>
          <h1 className="text-sm mb-1 uppercase tracking-widest">Suggest a Task</h1>
          <p className="font-sans text-xs text-[var(--color-text-muted)] mb-6">
            Know a great spot or activity? Submit it for review!
          </p>

          <div className="space-y-5">
            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">City *</label>
              <select value={cityId} onChange={(e) => setCityId(e.target.value)} className="w-full px-4 py-3 text-sm">
                {cities.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}{c.state ? `, ${c.state}` : ''}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Task Name *</label>
              <input
                value={name} onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Prince's Hot Chicken Shack"
                className="w-full px-4 py-3 text-sm"
                maxLength={255}
              />
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Category *</label>
              <div className="flex flex-wrap gap-2">
                {CATEGORY_OPTIONS.map((c) => (
                  <button
                    key={c} onClick={() => setCategory(c)}
                    className={`px-3 py-1.5 text-[9px] uppercase tracking-widest transition-colors border-2 ${
                      category === c
                        ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]'
                        : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Description</label>
              <textarea
                value={description} onChange={(e) => setDescription(e.target.value)}
                placeholder="What makes this place or activity special?"
                rows={2}
                className="w-full px-4 py-3 text-sm bg-white border-2 border-[var(--color-border)] rounded-md focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)] outline-none font-sans resize-none"
              />
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">What should the user do?</label>
              <textarea
                value={taskDescription} onChange={(e) => setTaskDescription(e.target.value)}
                placeholder="e.g. Try the original hot chicken sandwich"
                rows={2}
                className="w-full px-4 py-3 text-sm bg-white border-2 border-[var(--color-border)] rounded-md focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)] outline-none font-sans resize-none"
              />
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Address</label>
              <input
                value={address} onChange={(e) => setAddress(e.target.value)}
                placeholder="123 Main St, Nashville, TN"
                className="w-full px-4 py-3 text-sm"
              />
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Verification Type</label>
              <div className="flex gap-2">
                {VERIFICATION_TYPES.map((vt) => (
                  <button
                    key={vt} onClick={() => setVerificationType(vt)}
                    className={`flex-1 py-2 text-[9px] uppercase tracking-widest transition-colors border-2 ${
                      verificationType === vt
                        ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]'
                        : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
                    }`}
                  >
                    {vt}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Verification Hint</label>
              <input
                value={verificationHint} onChange={(e) => setVerificationHint(e.target.value)}
                placeholder="e.g. Take a photo of your plate"
                className="w-full px-4 py-3 text-sm"
              />
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Vibes</label>
              <div className="flex flex-wrap gap-2">
                {VIBE_OPTIONS.map((v) => (
                  <button
                    key={v} onClick={() => toggleVibe(v)}
                    className={`px-3 py-1.5 text-[9px] uppercase tracking-widest transition-colors border-2 ${
                      vibes.includes(v)
                        ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]'
                        : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
                    }`}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Price Level</label>
              <div className="flex gap-2">
                {[1, 2, 3, 4].map((p) => (
                  <button
                    key={p}
                    onClick={() => setPriceLevel(priceLevel === p ? null : p)}
                    className={`flex-1 py-2 text-[9px] uppercase tracking-widest transition-colors border-2 ${
                      priceLevel === p
                        ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary-dark)]'
                        : 'bg-white text-[var(--color-text-muted)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
                    }`}
                  >
                    {'$'.repeat(p)}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">
                Duration (minutes)
              </label>
              <input
                type="number" value={duration} onChange={(e) => setDuration(e.target.value)}
                placeholder="30" min={1}
                className="w-full px-4 py-3 text-sm"
              />
            </div>

            <div>
              <label className="text-[10px] text-[var(--color-text-muted)] block mb-2 uppercase tracking-widest">Pro Tips</label>
              <textarea
                value={proTips} onChange={(e) => setProTips(e.target.value)}
                placeholder="Any insider tips for this activity?"
                rows={2}
                className="w-full px-4 py-3 text-sm bg-white border-2 border-[var(--color-border)] rounded-md focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)] outline-none font-sans resize-none"
              />
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={submitting || !name.trim() || !category || !cityId}
            className="w-full mt-8 py-4 bg-[var(--color-primary)] text-white text-sm uppercase tracking-widest btn-retro flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {submitting ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
            {submitting ? 'Submitting...' : 'Submit for Review'}
          </button>
        </>
      ) : (
        <>
          <h1 className="text-sm mb-1 uppercase tracking-widest">My Submissions</h1>
          <p className="font-sans text-xs text-[var(--color-text-muted)] mb-4">Track the status of your suggestions</p>

          {mySubmissions.length === 0 ? (
            <div className="text-center py-12">
              <p className="font-sans text-xs text-[var(--color-text-muted)]">No submissions yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {mySubmissions.map((sub) => (
                <div key={sub.id} className="card-retro p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-bold text-sm">{sub.name}</h3>
                      <p className="text-[10px] text-[var(--color-text-muted)] mt-0.5">{sub.city_name} &middot; {sub.category}</p>
                    </div>
                    <div className="flex items-center gap-1 ml-2">
                      {statusIcon(sub.status)}
                      <span className={`text-[8px] uppercase tracking-widest ${
                        sub.status === 'approved' ? 'text-[var(--color-success)]' :
                        sub.status === 'rejected' ? 'text-[var(--color-error)]' :
                        'text-[var(--color-text-muted)]'
                      }`}>
                        {sub.status}
                      </span>
                    </div>
                  </div>
                  {sub.rejection_reason && (
                    <p className="font-sans text-[10px] text-[var(--color-error)] mt-1.5 bg-red-50 px-2 py-1 rounded">
                      {sub.rejection_reason}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
