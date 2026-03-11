"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import Sidebar from "@/components/admin/Sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const { isAuthenticated, hydrate } = useAuthStore();

    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    useEffect(() => {
        hydrate();
    }, [hydrate]);

    useEffect(() => {
        if (!isAuthenticated && pathname !== "/login") {
            router.push("/login");
        }
    }, [isAuthenticated, pathname, router]);

    // Login page renders without sidebar
    if (pathname === "/login") {
        return <>{children}</>;
    }

    if (!isAuthenticated) return null;

    return (
        <div className="flex min-h-screen bg-slate-50">
            <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
            <div className="flex-1 flex flex-col min-w-0 md:ml-64">
                {/* Mobile Top Bar */}
                <div className="md:hidden sticky top-0 z-30 flex items-center justify-between bg-white border-b border-slate-200 px-6 py-4 shadow-sm">
                    <div className="font-bold text-slate-900">Panel Admin</div>
                    <button
                        onClick={() => setIsSidebarOpen(true)}
                        className="p-2 -mr-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                </div>
                {/* Main Content Area */}
                <main className="flex-1 p-4 md:p-8 md:pt-6 overflow-x-hidden">
                    {children}
                </main>
            </div>
        </div>
    );
}
