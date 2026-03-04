"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAdminServices, createService, deleteService } from "@/lib/api";

export default function ServicesPage() {
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ name: "", price: "", duration_minutes: "30" });
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({ queryKey: ["admin-services"], queryFn: fetchAdminServices });
    const services = data?.data || [];

    const createMut = useMutation({
        mutationFn: () => createService({ name: form.name, price: Number(form.price), duration_minutes: Number(form.duration_minutes) }),
        onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["admin-services"] }); setShowForm(false); setForm({ name: "", price: "", duration_minutes: "30" }); },
    });

    const deleteMut = useMutation({
        mutationFn: deleteService,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-services"] }),
    });

    return (
        <div>
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Servicios</h1>
                <button onClick={() => setShowForm(!showForm)}
                    className="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700">
                    {showForm ? "Cancelar" : "+ Nuevo Servicio"}
                </button>
            </div>

            {showForm && (
                <form onSubmit={(e) => { e.preventDefault(); createMut.mutate(); }}
                    className="mt-4 bg-white rounded-2xl border border-slate-100 p-5 flex flex-wrap gap-4 items-end">
                    <div className="flex-1 min-w-[200px]">
                        <label className="block text-xs font-medium text-slate-600 mb-1">Nombre</label>
                        <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required
                            className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:border-indigo-500 outline-none" />
                    </div>
                    <div className="w-32">
                        <label className="block text-xs font-medium text-slate-600 mb-1">Precio ($)</label>
                        <input type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} required
                            className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:border-indigo-500 outline-none" />
                    </div>
                    <div className="w-32">
                        <label className="block text-xs font-medium text-slate-600 mb-1">Duración (min)</label>
                        <input type="number" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })}
                            className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:border-indigo-500 outline-none" />
                    </div>
                    <button type="submit" disabled={createMut.isPending}
                        className="px-6 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50">
                        {createMut.isPending ? "Creando..." : "Crear"}
                    </button>
                </form>
            )}

            <div className="mt-6 bg-white rounded-2xl border border-slate-100 overflow-x-auto">
                <table className="w-full min-w-[500px]">
                    <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
                        <tr>
                            <th className="text-left px-5 py-3 font-medium">Servicio</th>
                            <th className="text-left px-5 py-3 font-medium">Duración</th>
                            <th className="text-left px-5 py-3 font-medium">Precio</th>
                            <th className="text-right px-5 py-3 font-medium">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {isLoading ? [...Array(3)].map((_, i) => (
                            <tr key={i}><td colSpan={4} className="px-5 py-4"><div className="h-4 bg-slate-100 rounded animate-pulse" /></td></tr>
                        )) : services.map((svc) => (
                            <tr key={svc.id} className="hover:bg-slate-50/50">
                                <td className="px-5 py-3 text-sm font-medium text-slate-900">{svc.name}</td>
                                <td className="px-5 py-3 text-sm text-slate-500">{svc.duration_minutes} min</td>
                                <td className="px-5 py-3 text-sm font-semibold text-indigo-600">${svc.price.toLocaleString()}</td>
                                <td className="px-5 py-3 text-right">
                                    <button onClick={() => { if (confirm(`¿Eliminar "${svc.name}"?`)) deleteMut.mutate(svc.id); }}
                                        className="text-xs text-red-500 hover:text-red-700 font-medium">Eliminar</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
