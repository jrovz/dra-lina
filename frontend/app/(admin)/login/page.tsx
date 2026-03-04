"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();
    const setAuth = useAuthStore((s) => s.setAuth);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const res = await login(username, password);
            setAuth(res.user, res.access_token, res.refresh_token);
            router.push("/dashboard");
        } catch {
            setError("Credenciales inválidas");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 px-6">
            <div className="w-full max-w-sm">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white">Dra. Lina</h1>
                    <p className="mt-1 text-indigo-300 text-sm">Panel de Administración</p>
                </div>

                <form onSubmit={handleSubmit} className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-indigo-200 mb-1">Usuario</label>
                        <input
                            type="text" value={username} onChange={(e) => setUsername(e.target.value)}
                            className="w-full px-4 py-2.5 rounded-xl bg-white/10 border border-white/10 text-white placeholder-white/30 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 outline-none"
                            placeholder="admin"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-indigo-200 mb-1">Contraseña</label>
                        <input
                            type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-2.5 rounded-xl bg-white/10 border border-white/10 text-white placeholder-white/30 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 outline-none"
                            placeholder="••••••••"
                        />
                    </div>
                    {error && <p className="text-red-400 text-sm">{error}</p>}
                    <button
                        type="submit" disabled={loading}
                        className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold hover:shadow-lg hover:shadow-indigo-500/25 disabled:opacity-50 transition-all"
                    >
                        {loading ? "Ingresando..." : "Iniciar Sesión"}
                    </button>
                </form>
            </div>
        </div>
    );
}
