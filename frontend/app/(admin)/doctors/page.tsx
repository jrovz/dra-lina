"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAdminDoctors, createDoctor, deleteDoctor } from "@/lib/api";

export default function DoctorsPage() {
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ name: "", username: "", password: "", specialty: "", color: "#6366f1", bio: "" });
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({ queryKey: ["admin-doctors"], queryFn: fetchAdminDoctors });
    const doctors = data?.data || [];

    const createMut = useMutation({
        mutationFn: () => createDoctor(form),
        onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["admin-doctors"] }); setShowForm(false); setForm({ name: "", username: "", password: "", specialty: "", color: "#6366f1", bio: "" }); },
    });

    const deleteMut = useMutation({
        mutationFn: deleteDoctor,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-doctors"] }),
    });

    return (
        <div>
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Doctores</h1>
                <button onClick={() => setShowForm(!showForm)}
                    className="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700">
                    {showForm ? "Cancelar" : "+ Nuevo Doctor"}
                </button>
            </div>

            {showForm && (
                <form onSubmit={(e) => { e.preventDefault(); createMut.mutate(); }}
                    className="mt-4 bg-white rounded-2xl border border-slate-100 p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                        { label: "Nombre", field: "name" }, { label: "Usuario", field: "username" },
                        { label: "Contraseña", field: "password" }, { label: "Especialidad", field: "specialty" },
                    ].map(({ label, field }) => (
                        <div key={field}>
                            <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
                            <input value={form[field as keyof typeof form]} onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                                type={field === "password" ? "password" : "text"} required
                                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:border-indigo-500 outline-none" />
                        </div>
                    ))}
                    <div className="sm:col-span-2">
                        <label className="block text-xs font-medium text-slate-600 mb-1">Bio</label>
                        <textarea value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} rows={2}
                            className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:border-indigo-500 outline-none" />
                    </div>
                    <div className="sm:col-span-2">
                        <button type="submit" disabled={createMut.isPending}
                            className="px-6 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50">
                            {createMut.isPending ? "Creando..." : "Crear Doctor"}
                        </button>
                    </div>
                </form>
            )}

            <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {isLoading ? [...Array(3)].map((_, i) => (
                    <div key={i} className="bg-white rounded-2xl border p-5 animate-pulse"><div className="h-12 w-12 rounded-xl bg-slate-100" /></div>
                )) : doctors.map((doc) => (
                    <div key={doc.id} className="bg-white rounded-2xl border border-slate-100 p-5">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold" style={{ background: doc.color }}>
                                {doc.name.charAt(0)}
                            </div>
                            <div>
                                <p className="font-bold text-slate-900">{doc.name}</p>
                                <p className="text-sm text-indigo-600">{doc.specialty || "—"}</p>
                            </div>
                        </div>
                        <div className="mt-3 flex gap-2">
                            <button onClick={() => { if (confirm(`¿Eliminar a ${doc.name}?`)) deleteMut.mutate(doc.id); }}
                                className="text-xs text-red-500 hover:text-red-700 font-medium">Eliminar</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
