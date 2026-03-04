"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAdminPosts, deletePost } from "@/lib/api";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";

export default function PostsPage() {
    const [page, setPage] = useState(1);
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ["admin-posts", page],
        queryFn: () => fetchAdminPosts(page),
    });

    const deleteMutation = useMutation({
        mutationFn: deletePost,
        onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-posts"] }),
    });

    const posts = data?.data || [];
    const pagination = data?.pagination;

    return (
        <div>
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Blog Posts</h1>
                    <p className="text-slate-500 text-sm mt-1">{pagination?.total || 0} artículos</p>
                </div>
                <Link href="/posts/new"
                    className="px-5 py-2 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition-colors">
                    + Nuevo Post
                </Link>
            </div>

            <div className="mt-6 bg-white rounded-2xl border border-slate-100 overflow-x-auto">
                <table className="w-full min-w-[800px]">
                    <thead className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
                        <tr>
                            <th className="text-left px-5 py-3 font-medium">Título</th>
                            <th className="text-left px-5 py-3 font-medium">Categoría</th>
                            <th className="text-left px-5 py-3 font-medium">Estado</th>
                            <th className="text-left px-5 py-3 font-medium">Fecha</th>
                            <th className="text-right px-5 py-3 font-medium">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {isLoading ? (
                            [...Array(5)].map((_, i) => (
                                <tr key={i}><td colSpan={5} className="px-5 py-4"><div className="h-4 bg-slate-100 rounded animate-pulse" /></td></tr>
                            ))
                        ) : posts.map((post) => (
                            <tr key={post.id} className="hover:bg-slate-50/50 transition-colors">
                                <td className="px-5 py-3">
                                    <p className="font-medium text-slate-900 text-sm truncate max-w-xs">{post.title}</p>
                                </td>
                                <td className="px-5 py-3">
                                    {post.category && <span className="px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600 text-xs font-medium">{post.category}</span>}
                                </td>
                                <td className="px-5 py-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${post.is_published ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                                        }`}>
                                        {post.is_published ? "Publicado" : "Borrador"}
                                    </span>
                                </td>
                                <td className="px-5 py-3 text-xs text-slate-500">
                                    {post.created_at && format(new Date(post.created_at), "d MMM yyyy", { locale: es })}
                                </td>
                                <td className="px-5 py-3 text-right space-x-2">
                                    <Link href={`/posts/${post.id}`} className="text-xs font-medium text-indigo-600 hover:text-indigo-800">Editar</Link>
                                    <button onClick={() => { if (confirm("¿Eliminar este post?")) deleteMutation.mutate(post.id); }}
                                        className="text-xs font-medium text-red-500 hover:text-red-700">Eliminar</button>
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
