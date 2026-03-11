"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchDoctors, fetchServices, fetchDoctorSlots, createAppointment } from "@/lib/api";
import type { Doctor, Service } from "@/lib/types";
import { format } from "date-fns";
import { es } from "date-fns/locale";

type Step = "doctor" | "service" | "datetime" | "data" | "confirm";

interface BookingData {
    doctor: Doctor | null;
    service: Service | null;
    date: string;
    time: string;
    name: string;
    document_id: string;
    phone: string;
    email: string;
    age: string;
}

export default function BookingWizard() {
    const [step, setStep] = useState<Step>("doctor");
    const [data, setData] = useState<BookingData>({
        doctor: null, service: null, date: "", time: "",
        name: "", document_id: "", phone: "", email: "", age: "",
    });
    const [result, setResult] = useState<{ token: string } | null>(null);
    const [error, setError] = useState("");

    const { data: doctorsRes } = useQuery({ queryKey: ["doctors"], queryFn: fetchDoctors });
    const { data: servicesRes } = useQuery({ queryKey: ["services"], queryFn: fetchServices });

    const doctors = doctorsRes?.data || [];
    const services = servicesRes?.data || [];

    const { data: slotsRes, isLoading: slotsLoading } = useQuery({
        queryKey: ["slots", data.doctor?.id, data.date, data.service?.id],
        queryFn: () => fetchDoctorSlots(data.doctor!.id, data.date, data.service!.id),
        enabled: !!data.doctor && !!data.date && !!data.service,
    });
    const slots = slotsRes?.data || [];

    const steps: { key: Step; label: string }[] = [
        { key: "doctor", label: "Doctor" },
        { key: "service", label: "Servicio" },
        { key: "datetime", label: "Fecha" },
        { key: "data", label: "Datos" },
        { key: "confirm", label: "Confirmar" },
    ];

    const currentIdx = steps.findIndex((s) => s.key === step);

    async function handleSubmit() {
        if (!data.doctor || !data.service) return;
        setError("");
        try {
            const res = await createAppointment({
                name: data.name, document_id: data.document_id,
                phone: data.phone, age: Number(data.age),
                email: data.email || undefined,
                service_id: data.service.id, doctor_id: data.doctor.id,
                date: data.date, time: data.time,
            });
            setResult({ token: res.confirmation_token });
        } catch (err) {
            setError(err instanceof Error ? err.message : "Error al crear la cita");
        }
    }

    if (result) {
        return (
            <div className="text-center py-12">
                <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
                    <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <h2 className="mt-4 text-2xl font-bold text-slate-900">¡Cita Reservada!</h2>
                <p className="mt-2 text-slate-500">
                    Tu cita ha sido registrada. Recibirás confirmación pronto.
                </p>
            </div>
        );
    }

    return (
        <div>
            {/* Steps indicator */}
            <div className="flex items-center justify-center gap-2 mb-8">
                {steps.map((s, i) => (
                    <div key={s.key} className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${i <= currentIdx ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-400"
                            }`}>
                            {i + 1}
                        </div>
                        <span className={`hidden sm:block text-xs font-medium ${i <= currentIdx ? "text-indigo-600" : "text-slate-400"
                            }`}>{s.label}</span>
                        {i < steps.length - 1 && <div className="w-6 h-px bg-slate-200" />}
                    </div>
                ))}
            </div>

            {/* Step: Doctor */}
            {step === "doctor" && (
                <div>
                    <h2 className="text-xl font-bold text-slate-900 mb-4">Selecciona un doctor</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {doctors.map((doc) => (
                            <button key={doc.id} onClick={() => { setData({ ...data, doctor: doc }); setStep("service"); }}
                                className="p-4 rounded-xl border-2 text-left hover:border-indigo-500 hover:shadow-md transition-all">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg" style={{ background: doc.color }}>
                                        {doc.name.charAt(0)}
                                    </div>
                                    <div>
                                        <p className="font-bold text-slate-900">{doc.name}</p>
                                        <p className="text-sm text-indigo-600">{doc.specialty}</p>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Step: Service */}
            {step === "service" && (
                <div>
                    <h2 className="text-xl font-bold text-slate-900 mb-4">Selecciona un servicio</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {services.map((svc) => (
                            <button key={svc.id} onClick={() => { setData({ ...data, service: svc }); setStep("datetime"); }}
                                className="p-4 rounded-xl border-2 text-left hover:border-indigo-500 hover:shadow-md transition-all">
                                <p className="font-bold text-slate-900">{svc.name}</p>
                                <p className="text-sm text-slate-500">{svc.duration_minutes} min · ${svc.price.toLocaleString()}</p>
                            </button>
                        ))}
                    </div>
                    <button onClick={() => setStep("doctor")} className="mt-4 text-sm text-slate-500 hover:text-indigo-600">← Atrás</button>
                </div>
            )}

            {/* Step: Date & Time */}
            {step === "datetime" && (
                <div>
                    <h2 className="text-xl font-bold text-slate-900 mb-4">Fecha y hora</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Fecha</label>
                            <input type="date" value={data.date}
                                min={format(new Date(), "yyyy-MM-dd")}
                                onChange={(e) => setData({ ...data, date: e.target.value, time: "" })}
                                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none" />
                        </div>
                        {data.date && (
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">Horarios disponibles</label>
                                {slotsLoading ? (
                                    <p className="text-slate-400 text-sm">Cargando horarios...</p>
                                ) : slots.length > 0 ? (
                                    <div className="grid grid-cols-2 min-[400px]:grid-cols-3 sm:grid-cols-4 gap-3">
                                        {slots.map((slot: string) => (
                                            <button key={slot} onClick={() => setData({ ...data, time: slot })}
                                                className={`px-3 py-3 rounded-xl text-sm font-medium transition-all ${data.time === slot ? "bg-indigo-600 text-white shadow-md shadow-indigo-200" : "bg-white border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50 text-slate-700"
                                                    }`}>
                                                {slot}
                                            </button>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-orange-500 text-sm">No hay horarios disponibles para esta fecha.</p>
                                )}
                            </div>
                        )}
                    </div>
                    <div className="mt-8 flex gap-3">
                        <button onClick={() => setStep("service")} className="px-5 py-3 rounded-xl text-sm font-medium text-slate-500 hover:text-indigo-600 hover:bg-slate-50 transition-colors">← Atrás</button>
                        {data.time && (
                            <button onClick={() => setStep("data")}
                                className="flex-1 sm:flex-none px-6 py-3 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 shadow-md shadow-indigo-500/20 active:scale-95 transition-all text-center">
                                Continuar →
                            </button>
                        )}
                    </div>
                </div>
            )}

            {/* Step: Personal Data */}
            {step === "data" && (
                <div>
                    <h2 className="text-xl font-bold text-slate-900 mb-4">Tus datos</h2>
                    <div className="space-y-3">
                        {[
                            { label: "Nombre completo", field: "name" as const, type: "text", required: true },
                            { label: "Documento de identidad", field: "document_id" as const, type: "text", required: true },
                            { label: "Teléfono", field: "phone" as const, type: "tel", required: true },
                            { label: "Email (opcional)", field: "email" as const, type: "email", required: false },
                            { label: "Edad", field: "age" as const, type: "number", required: true },
                        ].map(({ label, field, type, required }) => (
                            <div key={field}>
                                <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
                                <input type={type} required={required} value={data[field]}
                                    onChange={(e) => setData({ ...data, [field]: e.target.value })}
                                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none" />
                            </div>
                        ))}
                    </div>
                    <div className="mt-8 flex gap-3">
                        <button onClick={() => setStep("datetime")} className="px-5 py-3 rounded-xl text-sm font-medium text-slate-500 hover:text-indigo-600 hover:bg-slate-50 transition-colors">← Atrás</button>
                        <button onClick={() => setStep("confirm")}
                            disabled={!data.name || !data.document_id || !data.phone || !data.age}
                            className="flex-1 sm:flex-none px-6 py-3 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 shadow-md disabled:opacity-50 disabled:shadow-none active:scale-[0.98] transition-all text-center">
                            Revisar →
                        </button>
                    </div>
                </div>
            )}

            {/* Step: Confirm */}
            {step === "confirm" && (
                <div>
                    <h2 className="text-xl font-bold text-slate-900 mb-4">Confirmar reserva</h2>
                    <div className="bg-slate-50 rounded-2xl p-5 space-y-3 text-sm">
                        <div className="flex justify-between"><span className="text-slate-500">Doctor</span><span className="font-medium text-slate-900">{data.doctor?.name}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Servicio</span><span className="font-medium text-slate-900">{data.service?.name}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Fecha</span><span className="font-medium text-slate-900">
                            {data.date && format(new Date(data.date + "T12:00:00"), "d 'de' MMMM, yyyy", { locale: es })}
                        </span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Hora</span><span className="font-medium text-slate-900">{data.time}</span></div>
                        <hr className="border-slate-200" />
                        <div className="flex justify-between"><span className="text-slate-500">Paciente</span><span className="font-medium text-slate-900">{data.name}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Documento</span><span className="font-medium text-slate-900">{data.document_id}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Teléfono</span><span className="font-medium text-slate-900">{data.phone}</span></div>
                    </div>
                    {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
                    <div className="mt-8 flex gap-3 flex-col sm:flex-row">
                        <button onClick={() => setStep("data")} className="order-2 sm:order-1 px-5 py-3 rounded-xl text-sm font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 transition-colors">← Atrás</button>
                        <button onClick={handleSubmit}
                            className="order-1 sm:order-2 flex-1 px-8 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-bold shadow-lg shadow-indigo-500/30 hover:shadow-xl active:scale-[0.98] transition-all">
                            Confirmar Cita
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
