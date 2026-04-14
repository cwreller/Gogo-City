import api from './client';

export interface City {
  id: string;
  name: string;
  state: string | null;
  country: string;
}

export interface CuratedTask {
  id: string;
  name: string;
  category: string;
  description?: string;
  address?: string;
  task_description?: string;
  verification_type: string;
  verification_hint?: string;
  vibe_tags: string[];
  price_level?: number;
  avg_duration_minutes?: number;
  xp: number;
  lat?: number;
  lng?: number;
  is_active: boolean;
}

export async function listCities() {
  const { data } = await api.get<City[]>('/cities/');
  return data;
}

export async function listCuratedTasks(cityId: string) {
  const { data } = await api.get<CuratedTask[]>(`/cities/${cityId}/tasks`);
  return data;
}
