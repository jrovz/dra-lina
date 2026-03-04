"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import Sidebar from "@/components/admin/Sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const { isAuthenticated, hydrate } = useAuthStore();

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
            <Sidebar />
            <main className="flex-1 min-w-0 ml-64 p-8 pt-6">{children}</main>
        </div>
    );
}
