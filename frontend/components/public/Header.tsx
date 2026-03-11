"use client";

import Link from "next/link";
import { useState } from "react";
import { usePathname } from "next/navigation";

export default function Header() {
    const [open, setOpen] = useState(false);
    const pathname = usePathname();

    const isAdminPath = ["/login", "/dashboard", "/posts", "/doctors", "/services", "/appointments"].some(path => pathname?.startsWith(path));
    if (isAdminPath) return null;

    return (
        <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-lg border-b border-slate-200/60">
            <nav className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
                <Link
                    href="/"
                    className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent"
                >
                    Dra. Lina
                </Link>

                {/* Desktop */}
                <ul className="hidden md:flex items-center gap-8">
                    <li>
                        <Link
                            href="/"
                            className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors"
                        >
                            Inicio
                        </Link>
                    </li>
                    <li>
                        <Link
                            href="/blog"
                            className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors"
                        >
                            Blog de Salud
                        </Link>
                    </li>
                    <li>
                        <Link
                            href="/doctores"
                            className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors"
                        >
                            Doctores
                        </Link>
                    </li>
                    <li>
                        <Link
                            href="/reservar"
                            className="px-5 py-2 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-sm font-semibold hover:shadow-lg hover:shadow-indigo-500/25 transition-all duration-300"
                        >
                            Agendar Cita
                        </Link>
                    </li>
                </ul>

                {/* Mobile toggle */}
                <button
                    className="md:hidden p-2 text-slate-600"
                    onClick={() => setOpen(!open)}
                    aria-label="Menu"
                >
                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        {open ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        )}
                    </svg>
                </button>
            </nav>

            {/* Mobile menu */}
            {open && (
                <div className="md:hidden absolute top-16 left-0 right-0 bg-white/95 backdrop-blur-xl border-b border-slate-200/60 shadow-xl px-6 py-6 space-y-2">
                    <Link href="/" className="block py-3 text-slate-700 font-medium hover:text-indigo-600 transition-colors" onClick={() => setOpen(false)}>
                        Inicio
                    </Link>
                    <Link href="/blog" className="block py-3 text-slate-700 font-medium hover:text-indigo-600 transition-colors" onClick={() => setOpen(false)}>
                        Blog de Salud
                    </Link>
                    <Link href="/doctores" className="block py-3 text-slate-700 font-medium hover:text-indigo-600 transition-colors" onClick={() => setOpen(false)}>
                        Doctores
                    </Link>
                    <div className="pt-4">
                        <Link
                            href="/reservar"
                            className="block text-center py-4 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold shadow-lg shadow-indigo-500/25 active:scale-95 transition-all"
                            onClick={() => setOpen(false)}
                        >
                            Agendar Cita
                        </Link>
                    </div>
                </div>
            )}
        </header>
    );
}
