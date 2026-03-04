"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Footer() {
    const pathname = usePathname();
    const isAdminPath = ["/login", "/dashboard", "/posts", "/doctors", "/services", "/appointments"].some(path => pathname?.startsWith(path));

    if (isAdminPath) return null;

    return (
        <footer className="bg-slate-900 text-slate-300">
            <div className="max-w-6xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Brand */}
                <div>
                    <h3 className="text-xl font-bold text-white mb-3">Dra. Lina</h3>
                    <p className="text-sm leading-relaxed text-slate-400">
                        Especialista en Salud Familiar y Ecografía Clínica. Cuidado integral
                        para toda la familia en Rovira, Tolima.
                    </p>
                </div>

                {/* Nav */}
                <div>
                    <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
                        Navegación
                    </h4>
                    <ul className="space-y-2 text-sm">
                        <li><Link href="/" className="hover:text-indigo-400 transition-colors">Inicio</Link></li>
                        <li><Link href="/blog" className="hover:text-indigo-400 transition-colors">Blog de Salud</Link></li>
                        <li><Link href="/doctores" className="hover:text-indigo-400 transition-colors">Doctores</Link></li>
                        <li><Link href="/reservar" className="hover:text-indigo-400 transition-colors">Agendar Cita</Link></li>
                    </ul>
                </div>

                {/* Legal */}
                <div>
                    <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
                        Legal
                    </h4>
                    <ul className="space-y-2 text-sm">
                        <li><Link href="/terminos" className="hover:text-indigo-400 transition-colors">Términos y Condiciones</Link></li>
                    </ul>
                </div>
            </div>

            <div className="border-t border-slate-800">
                <div className="max-w-6xl mx-auto px-6 py-4">
                    <p className="text-center text-xs text-slate-500">
                        © {new Date().getFullYear()} Dra. Lina María Valencia Arias. Todos los
                        derechos reservados.
                    </p>
                </div>
            </div>
        </footer>
    );
}
