import api from './client';
import { Instance, InstanceTask } from './instances';

export interface SharedRoutePreview {
  id: string;
  title: string;
  description?: string;
  share_code?: string;
  estimated_duration_minutes?: number;
  vibe_tags: string[];
  tasks: InstanceTask[];
}

export async function previewSharedRoute(shareCode: string) {
  const { data } = await api.get<SharedRoutePreview>(`/routes/share/${shareCode}`);
  return data;
}

export async function importSharedRoute(shareCode: string) {
  const { data } = await api.post<Instance>(`/routes/import/${shareCode}`);
  return data;
}
