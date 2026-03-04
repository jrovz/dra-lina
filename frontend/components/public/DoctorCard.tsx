import Link from "next/link";
import type { Doctor } from "@/lib/types";

export default function DoctorCard({ doctor }: { doctor: Doctor }) {
    return (
        <div className="group relative bg-white rounded-2xl border border-slate-100 p-6 hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-1 transition-all duration-300">
            <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shadow-lg"
                style={{ background: doctor.color }}
            >
                {doctor.name.charAt(0)}
            </div>
            <h3 className="mt-4 text-lg font-bold text-slate-900">{doctor.name}</h3>
            <p className="text-sm font-medium text-indigo-600">{doctor.specialty}</p>
            {doctor.bio && (
                <p className="mt-3 text-sm text-slate-500 line-clamp-3 leading-relaxed">
                    {doctor.bio}
                </p>
            )}
            <Link
                href="/reservar"
                className="mt-4 inline-flex items-center gap-1 text-sm font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
            >
                Agendar con {doctor.name.split(" ")[0]}
                <span className="group-hover:translate-x-1 transition-transform">→</span>
            </Link>
        </div>
    );
}
