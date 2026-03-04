"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchDashboardStats } from "@/lib/api";

function StatsCard({ label, value, color }: { label: string; value: number; color: string }) {
    return (
        <div className="bg-white rounded-2xl border border-slate-100 p-5 hover:shadow-md transition-shadow">
            <p className="text-sm font-medium text-slate-500">{label}</p>
            <p className={`mt-1 text-3xl font-bold ${color}`}>{value}</p>
        </div>
    );
}

export default function DashboardPage() {
    const { data, isLoading } = useQuery({
        queryKey: ["dashboard-stats"],
        queryFn: fetchDashboardStats,
        refetchInterval: 30000,
    });

    const stats = data?.data;

    return (
        <div>
            <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            <p className="text-slate-500 text-sm mt-1">Resumen del consultorio</p>

            {isLoading ? (
                <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="bg-white rounded-2xl border border-slate-100 p-5 animate-pulse">
                            <div className="h-4 w-24 bg-slate-100 rounded" />
                            <div className="mt-2 h-8 w-16 bg-slate-100 rounded" />
                        </div>
                    ))}
                </div>
            ) : stats && (
                <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    <StatsCard label="Citas hoy" value={stats.appointments_today} color="text-indigo-600" />
                    <StatsCard label="Citas pendientes" value={stats.appointments_pending} color="text-amber-600" />
                    <StatsCard label="Posts publicados" value={stats.posts_published} color="text-emerald-600" />
                    <StatsCard label="Posts borrador" value={stats.posts_draft} color="text-slate-600" />
                    <StatsCard label="Doctores" value={stats.doctors_count} color="text-violet-600" />
                    <StatsCard label="Pacientes" value={stats.patients_count} color="text-cyan-600" />
                </div>
            )}
        </div>
    );
}
