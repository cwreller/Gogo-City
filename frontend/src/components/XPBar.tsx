import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const LEVEL_THRESHOLDS = [0, 200, 500, 1000, 1750, 2750, 4000, 5500, 7500, 10000];

function getNextThreshold(xp: number) {
  for (const t of LEVEL_THRESHOLDS) {
    if (xp < t) return t;
  }
  return LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1];
}

function getPrevThreshold(xp: number) {
  let prev = 0;
  for (const t of LEVEL_THRESHOLDS) {
    if (xp < t) return prev;
    prev = t;
  }
  return prev;
}

interface Props {
  xp: number;
  level: number;
  compact?: boolean;
  expandable?: boolean;
}

export default function XPBar({ xp, level, compact, expandable }: Props) {
  const [expanded, setExpanded] = useState(false);
  const prev = getPrevThreshold(xp);
  const next = getNextThreshold(xp);
  const progress = next > prev ? ((xp - prev) / (next - prev)) * 100 : 100;

  if (compact && !expandable) {
    return (
      <div className="flex items-center gap-2">
        <span className="text-[10px] bg-[var(--color-primary)] text-white px-2 py-0.5 border-2 border-[var(--color-primary-dark)] uppercase">
          Lv.{level}
        </span>
        <div className="flex-1 progress-retro h-2">
          <div className="progress-retro-fill h-full transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
        <span className="text-[10px] text-[var(--color-text-muted)]">{xp} XP</span>
      </div>
    );
  }

  if (expandable && !expanded) {
    return (
      <button
        onClick={() => setExpanded(true)}
        className="w-full card-retro p-3 flex items-center gap-3 text-left transition-colors hover:bg-[var(--color-surface-light)]"
      >
        <span className="text-[10px] bg-[var(--color-primary)] text-white px-2 py-0.5 border-2 border-[var(--color-primary-dark)] uppercase">
          Lv.{level}
        </span>
        <div className="flex-1 progress-retro h-2">
          <div className="progress-retro-fill h-full transition-all duration-500" style={{ width: `${progress}%` }} />
        </div>
        <span className="text-[10px] text-[var(--color-text-muted)]">{xp} XP</span>
        <ChevronDown size={14} className="text-[var(--color-text-muted)]" />
      </button>
    );
  }

  return (
    <div
      className={`card-retro p-4 ${expandable ? 'cursor-pointer hover:bg-[var(--color-surface-light)]' : ''}`}
      style={{ boxShadow: '0 4px 12px rgba(229, 57, 53, 0.08)' }}
      onClick={expandable ? () => setExpanded(false) : undefined}
    >
      <div className="flex justify-between items-center mb-3">
        <span className="text-sm bg-[var(--color-primary)] text-white px-3 py-1 rounded-sm border-2 border-[var(--color-primary-dark)] uppercase tracking-widest"
          style={{ boxShadow: '0 2px 8px rgba(229, 57, 53, 0.3)' }}>
          Level {level}
        </span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-[var(--color-primary)]">{xp} XP</span>
          {expandable && <ChevronDown size={14} className="text-[var(--color-text-muted)] rotate-180 transition-transform" />}
        </div>
      </div>
      <div className="progress-retro h-5">
        <div className="progress-retro-fill h-full" style={{ width: `${progress}%` }} />
      </div>
      <div className="flex justify-between mt-1.5">
        <span className="font-sans text-[9px] text-[var(--color-text-muted)]">{prev} XP</span>
        <span className="font-sans text-[9px] text-[var(--color-text-muted)]">{next} XP</span>
      </div>
    </div>
  );
}
