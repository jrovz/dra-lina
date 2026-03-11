import { fetchDoctors } from "@/lib/api";
import DoctorCard from "@/components/public/DoctorCard";
import type { Doctor } from "@/lib/types";

export const metadata = {
    title: "Nuestros Doctores",
    description: "Conoce al equipo médico del consultorio de la Dra. Lina en Rovira, Tolima.",
};

export default async function DoctoresPage() {
    let doctors: Doctor[] = [];

    try {
        const res = await fetchDoctors();
        doctors = res.data;
    } catch { /* API unavailable */ }

    return (
        <div className="pt-20 pb-12 md:pt-24 md:pb-16">
            <div className="max-w-6xl mx-auto px-6">
                <h1 className="text-3xl md:text-4xl font-bold text-slate-900">
                    Nuestro Equipo Médico
                </h1>
                <p className="mt-3 text-slate-500 text-lg">
                    Profesionales comprometidos con tu salud y bienestar.
                </p>

                {doctors.length > 0 ? (
                    <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {doctors.map((doc) => (
                            <DoctorCard key={doc.id} doctor={doc} />
                        ))}
                    </div>
                ) : (
                    <div className="mt-16 text-center text-slate-400">
                        <p>No hay doctores registrados aún.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
