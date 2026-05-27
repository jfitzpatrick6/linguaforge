const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson?.detail) {
        message = typeof errJson.detail === 'string'
          ? errJson.detail
          : JSON.stringify(errJson.detail, null, 2);
      } else {
        message = JSON.stringify(errJson, null, 2);
      }
    } catch {
      const txt = await res.text().catch(() => '');
      if (txt) message = txt;
      else message = `HTTP error! status: ${res.status}`;
    }
    throw new Error(message);
  }

  return res.json();
}

// Example typed methods (we can expand these)
export const api = {
  // Profile / Onboarding
  onboard: (data: any) => apiFetch('/api/onboarding', { method: 'POST', body: JSON.stringify(data) }),
  startAssessment: (data: { user_id: string; target_language: string }) =>
    apiFetch('/api/onboarding/start-assessment', { method: 'POST', body: JSON.stringify(data) }),
  submitAssessment: (data: any) =>
    apiFetch('/api/onboarding/submit-assessment', { method: 'POST', body: JSON.stringify(data) }),

  // Curriculum
  seedCurriculum: (userId: string, language?: string) =>
    apiFetch(`/api/curriculum/seed/${userId}${language ? `?language=${language}` : ''}`, { method: 'POST' }),
  getCurriculumOverview: (userId: string) => apiFetch(`/api/curriculum/overview/${userId}`),
  adaptCurriculum: (userId: string, language?: string) =>
    apiFetch(`/api/curriculum/adapt/${userId}${language ? `?language=${language}` : ''}`, { method: 'POST' }),

  // Lessons
  generateLesson: (data: any) => apiFetch('/api/lessons/generate', { method: 'POST', body: JSON.stringify(data) }),
  generatePractice: (data: any) => apiFetch('/api/lessons/practice/generate', { method: 'POST', body: JSON.stringify(data) }),
  submitPractice: (data: any) => apiFetch('/api/lessons/practice/submit', { method: 'POST', body: JSON.stringify(data) }),
};
