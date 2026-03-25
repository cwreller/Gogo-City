import api from './client';

export interface SubmitTaskPayload {
  city_id: string;
  name: string;
  description?: string;
  address?: string;
  task_description?: string;
  verification_hint?: string;
  verification_type: string;
  category: string;
  vibe_tags: string[];
  price_level?: number | null;
  avg_duration_minutes?: number | null;
  pro_tips?: string;
}

export interface Submission {
  id: string;
  submitted_by: string;
  submitter_username: string;
  city_id: string;
  city_name: string;
  name: string;
  description: string | null;
  address: string | null;
  task_description: string | null;
  verification_hint: string | null;
  verification_type: string;
  category: string;
  vibe_tags: string[];
  price_level: number | null;
  avg_duration_minutes: number | null;
  pro_tips: string | null;
  status: string;
  rejection_reason: string | null;
  created_at: string;
}

export async function submitTask(payload: SubmitTaskPayload) {
  const { data } = await api.post<Submission>('/submissions/', payload);
  return data;
}

export async function getMySubmissions() {
  const { data } = await api.get<Submission[]>('/submissions/mine');
  return data;
}

export async function getSubmissions(status = 'pending') {
  const { data } = await api.get<Submission[]>('/submissions/', { params: { status } });
  return data;
}

export async function reviewSubmission(id: string, action: 'approve' | 'reject', opts?: { rejection_reason?: string; xp?: number }) {
  const { data } = await api.patch<Submission>(`/submissions/${id}`, { action, ...opts });
  return data;
}
