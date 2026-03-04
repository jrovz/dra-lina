/**
 * API client with JWT interceptor.
 * In dev: SSR uses direct Flask URL, client uses Next.js rewrites proxy.
 * In prod: same domain via Nginx.
 */

const API_BASE =
    typeof window === 'undefined'
        ? (process.env.INTERNAL_API_URL || 'http://localhost:5000')
        : (process.env.NEXT_PUBLIC_API_URL || '');

async function request<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
    };

    // Attach JWT if available (client-side only)
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
    }
    // Timeout: 5s for SSR, 30s for client
    const timeoutMs = typeof window === 'undefined' ? 5000 : 30000;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    const res = await fetch(url, { ...options, headers, signal: controller.signal });
    clearTimeout(timer);

    if (res.status === 401 && typeof window !== 'undefined') {
        // Try refresh
        const refreshed = await tryRefreshToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${localStorage.getItem('access_token')}`;
            const retry = await fetch(url, { ...options, headers });
            if (!retry.ok) throw new ApiError(retry.status, await retry.text());
            return retry.json();
        }
        // Redirect to login
        window.location.href = '/login';
        throw new ApiError(401, 'Session expired');
    }

    if (!res.ok) {
        const body = await res.text();
        throw new ApiError(res.status, body);
    }

    return res.json();
}

async function tryRefreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
        const res = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${refreshToken}`,
            },
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('access_token', data.access_token);
            return true;
        }
    } catch { /* ignore */ }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return false;
}

export class ApiError extends Error {
    status: number;
    constructor(status: number, body: string) {
        super(`API Error ${status}: ${body}`);
        this.status = status;
    }
}

// --- Public Endpoints ---

import type {
    PaginatedResponse, ApiResponse, BlogPostListItem, BlogPost,
    Doctor, Service, LoginResponse, DashboardStats, Appointment, TaskStatus
} from './types';

export async function fetchPosts(page = 1, category?: string) {
    const params = new URLSearchParams({ page: String(page) });
    if (category) params.set('category', category);
    return request<PaginatedResponse<BlogPostListItem>>(`/api/v1/blog/posts?${params}`);
}

export async function fetchPostBySlug(slug: string) {
    return request<ApiResponse<BlogPost>>(`/api/v1/blog/posts/${slug}`);
}

export async function fetchDoctors() {
    return request<ApiResponse<Doctor[]>>('/api/v1/doctors');
}

export async function fetchDoctorSlots(doctorId: number, date: string, serviceId: number) {
    const params = new URLSearchParams({ date, service_id: String(serviceId) });
    return request<ApiResponse<string[]>>(`/api/v1/doctors/${doctorId}/slots?${params}`);
}

export async function fetchServices() {
    return request<ApiResponse<Service[]>>('/api/v1/services');
}

export async function createAppointment(data: {
    name: string; document_id: string; phone: string; age: number;
    email?: string; service_id: number; doctor_id: number; date: string; time: string;
}) {
    return request<{ data: Appointment; confirmation_token: string }>('/api/v1/appointments', {
        method: 'POST', body: JSON.stringify(data),
    });
}

// --- Auth ---

export async function login(username: string, password: string) {
    return request<LoginResponse>('/api/v1/auth/login', {
        method: 'POST', body: JSON.stringify({ username, password }),
    });
}

export async function logout() {
    return request<{ message: string }>('/api/v1/auth/logout', { method: 'DELETE' });
}

export async function fetchMe() {
    return request<{ id: number; username: string; role: string; email: string | null }>('/api/v1/auth/me');
}

// --- Admin ---

export async function fetchDashboardStats() {
    return request<ApiResponse<DashboardStats>>('/api/v1/admin/dashboard/stats');
}

export async function fetchAdminPosts(page = 1) {
    return request<PaginatedResponse<BlogPostListItem>>(`/api/v1/admin/posts?page=${page}`);
}

export async function createPost(data: Partial<BlogPost>) {
    return request<ApiResponse<BlogPost>>('/api/v1/admin/posts', {
        method: 'POST', body: JSON.stringify(data),
    });
}

export async function updatePost(id: number, data: Partial<BlogPost>) {
    return request<ApiResponse<BlogPost>>(`/api/v1/admin/posts/${id}`, {
        method: 'PUT', body: JSON.stringify(data),
    });
}

export async function deletePost(id: number) {
    return request<{ message: string }>(`/api/v1/admin/posts/${id}`, { method: 'DELETE' });
}

export async function fetchAdminDoctors() {
    return request<ApiResponse<Doctor[]>>('/api/v1/admin/doctors');
}

export async function createDoctor(data: { name: string; username: string; password: string; specialty: string; color?: string; bio?: string }) {
    return request<ApiResponse<Doctor>>('/api/v1/admin/doctors', {
        method: 'POST', body: JSON.stringify(data),
    });
}

export async function deleteDoctor(id: number) {
    return request<{ message: string }>(`/api/v1/admin/doctors/${id}`, { method: 'DELETE' });
}

export async function fetchAdminAppointments(page = 1, doctorId?: number, status?: string) {
    const params = new URLSearchParams({ page: String(page) });
    if (doctorId) params.set('doctor_id', String(doctorId));
    if (status) params.set('status', status);
    return request<PaginatedResponse<Appointment>>(`/api/v1/admin/appointments?${params}`);
}

export async function updateAppointmentStatus(id: number, status: string) {
    return request<ApiResponse<{ id: number; status: string }>>(`/api/v1/admin/appointments/${id}`, {
        method: 'PUT', body: JSON.stringify({ status }),
    });
}

export async function fetchAdminServices() {
    return request<ApiResponse<Service[]>>('/api/v1/admin/services');
}

export async function createService(data: { name: string; price: number; duration_minutes?: number }) {
    return request<ApiResponse<Service>>('/api/v1/admin/services', {
        method: 'POST', body: JSON.stringify(data),
    });
}

export async function deleteService(id: number) {
    return request<{ message: string }>(`/api/v1/admin/services/${id}`, { method: 'DELETE' });
}

// --- AI ---

export async function aiResearch(topic: string, model = 'gpt-4o') {
    return request<{ research: unknown }>('/api/v1/ai/research', {
        method: 'POST', body: JSON.stringify({ topic, model }),
    });
}

export async function aiGenerateDraft(topic: string, model = 'gpt-4o', research?: unknown) {
    return request<{ content: unknown }>('/api/v1/ai/generate-draft', {
        method: 'POST', body: JSON.stringify({ topic, model, research }),
    });
}

export async function aiGenerateImage(title: string, model = 'dall-e-3') {
    return request<{ image_url: string }>('/api/v1/ai/generate-image', {
        method: 'POST', body: JSON.stringify({ title, model }),
    });
}

export async function aiRefineBlock(content: string, action: string, context = '', model = 'gpt-4o') {
    return request<{ refined_content: string }>('/api/v1/ai/refine-block', {
        method: 'POST', body: JSON.stringify({ content, action, context, model }),
    });
}

export async function aiSeoAnalyze(title: string, content: string, keywords: string[] = []) {
    return request<unknown>('/api/v1/ai/seo-analyze', {
        method: 'POST', body: JSON.stringify({ title, content, keywords }),
    });
}

// --- Tasks (Celery polling) ---

export async function fetchTaskStatus(taskId: string) {
    return request<TaskStatus>(`/api/v1/tasks/${taskId}`);
}
