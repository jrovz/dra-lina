/**
 * Global auth state with Zustand.
 * Persists JWT tokens in localStorage.
 */
import { create } from 'zustand';
import type { AuthUser } from './types';

interface AuthState {
    user: AuthUser | null;
    isAuthenticated: boolean;
    setAuth: (user: AuthUser, accessToken: string, refreshToken: string) => void;
    clearAuth: () => void;
    hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,

    setAuth: (user, accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('user', JSON.stringify(user));
        set({ user, isAuthenticated: true });
    },

    clearAuth: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        set({ user: null, isAuthenticated: false });
    },

    hydrate: () => {
        if (typeof window === 'undefined') return;
        const stored = localStorage.getItem('user');
        const token = localStorage.getItem('access_token');
        if (stored && token) {
            try {
                set({ user: JSON.parse(stored), isAuthenticated: true });
            } catch {
                set({ user: null, isAuthenticated: false });
            }
        }
    },
}));
