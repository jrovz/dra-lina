/**
 * TypeScript types mirroring the Flask backend Marshmallow schemas.
 */

export interface BlogPost {
    id: number;
    title: string;
    slug: string | null;
    content: string;
    featured_image_url: string;
    seo_keywords: string;
    references: string;
    category: string | null;
    created_at: string;
    updated_at: string;
    is_published: boolean;
}

export interface BlogPostListItem {
    id: number;
    title: string;
    slug: string | null;
    featured_image_url: string;
    category: string | null;
    created_at: string;
    is_published: boolean;
}

export interface Doctor {
    id: number;
    username: string;
    name: string;
    specialty: string;
    bio: string;
    color: string;
}

export interface Service {
    id: number;
    name: string;
    duration_minutes: number;
    price: number;
}

export interface Appointment {
    id: number;
    patient_name: string;
    service_name: string;
    doctor_name: string;
    start_time: string;
    status: string;
    created_at: string;
}

export interface DashboardStats {
    appointments_today: number;
    appointments_pending: number;
    posts_published: number;
    posts_draft: number;
    doctors_count: number;
    patients_count: number;
}

export interface AuthUser {
    id: number;
    username: string;
    role: string;
    email: string | null;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    user: AuthUser;
}

export interface Pagination {
    page: number;
    per_page: number;
    total: number;
    pages: number;
}

export interface PaginatedResponse<T> {
    data: T[];
    pagination: Pagination;
}

export interface ApiResponse<T> {
    data: T;
}

export interface TaskStatus {
    task_id: string;
    state: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE';
    status: string;
    result?: unknown;
    error?: string;
}
