"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAdminAppointments, updateAppointmentStatus } from "@/lib/api";
import { format } from "date-fns";
import { es } from "date-fns/locale";

const STATUS_COLORS: Record<string, string> = {
    pendiente: "bg-amber-50 text-amber-700",
    confirmada: "bg-emerald-50 text-emerald-700",
    cancelada: "bg-red-50 text-red-700",
    completada: "bg-blue-50 text-blue-700",
};

export default function AppointmentsPage() {
    const [page, setPage] = useState(1);
    const [filterStatus, setFilterStatus] = useState("");
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ["admin-appointments", page, filterStatus],
        queryFn: () => fetchAdminAppointments(page, undefined, filterStatus || undefined),
    });

    const statusMut = useMutation({
        mutationFn: ({ id, status }: { id: number; status: string }) => updateAppointmentStatus(id, status),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-appointments"] }),
    });

    const appointments = data?.data || [];
    const pagination = data?.pagination;

    return (
        <div>
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Citas</h1>
                <select value={filterStatus} onChange={(e) => { setFilterStatus(e.target.value); setPage(1); }}
                    className="px-3 py-2 border border-slate-200 rounded-xl text-sm focus:border-indigo-500 outline-none">
                    <option value="">Todas</option>
                    <option value="pendiente">Pendientes</option>
                    <option value="confirmada">Confirmadas</option>
                    <option value="completada">Completadas</option>
                    <option value="cancelada">Canceladas</option>
                </select>
            </div>

            <div className="mt-6 bg-white rounded-2xl border border-slate-100 overflow-x-auto">
                <table className="w-full min-w-[800px]">
                    <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
                        <tr>
                            <th className="text-left px-5 py-3 font-medium">Paciente</th>
                            <th className="text-left px-5 py-3 font-medium">Servicio</th>
                            <th className="text-left px-5 py-3 font-medium">Doctor</th>
                            <th className="text-left px-5 py-3 font-medium">Fecha</th>
                            <th className="text-left px-5 py-3 font-medium">Estado</th>
                            <th className="text-right px-5 py-3 font-medium">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {isLoading ? [...Array(5)].map((_, i) => (
                            <tr key={i}><td colSpan={6} className="px-5 py-4"><div className="h-4 bg-slate-100 rounded animate-pulse" /></td></tr>
                        )) : appointments.map((appt) => (
                            <tr key={appt.id} className="hover:bg-slate-50/50">
                                <td className="px-5 py-3 text-sm font-medium text-slate-900">{appt.patient_name}</td>
                                <td className="px-5 py-3 text-sm text-slate-500">{appt.service_name}</td>
                                <td className="px-5 py-3 text-sm text-slate-500">{appt.doctor_name}</td>
                                <td className="px-5 py-3 text-xs text-slate-500">
                                    {appt.start_time && format(new Date(appt.start_time), "d MMM yyyy HH:mm", { locale: es })}
                                </td>
                                <td className="px-5 py-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[appt.status] || "bg-slate-100 text-slate-600"}`}>
                                        {appt.status}
                                    </span>
                                </td>
                                <td className="px-5 py-3 text-right">
                                    <select value={appt.status}
                                        onChange={(e) => statusMut.mutate({ id: appt.id, status: e.target.value })}
                                        className="text-xs border border-slate-200 rounded-lg px-2 py-1 focus:border-indigo-500 outline-none">
                                        <option value="pendiente">Pendiente</option>
                                        <option value="confirmada">Confirmada</option>
                                        <option value="completada">Completada</option>
                                        <option value="cancelada">Cancelada</option>
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {pagination && pagination.pages > 1 && (
                <div className="mt-4 flex justify-center gap-2">
                    {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((p) => (
                        <button key={p} onClick={() => setPage(p)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium ${p === page ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
                            {p}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
