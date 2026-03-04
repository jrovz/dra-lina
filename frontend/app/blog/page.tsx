import Link from "next/link";
import { fetchPosts } from "@/lib/api";
import type { BlogPostListItem } from "@/lib/types";
import BlogCard from "@/components/public/BlogCard";

export const metadata = {
    title: "Blog de Salud",
    description: "Artículos sobre medicina, ecografía y salud familiar escritos por la Dra. Lina María Valencia.",
};

export default async function BlogPage({
    searchParams,
}: {
    searchParams: Promise<{ page?: string; category?: string }>;
}) {
    const params = await searchParams;
    const page = Number(params.page) || 1;
    const category = params.category;

    let posts: BlogPostListItem[] = [];
    let pagination = { page: 1, per_page: 10, total: 0, pages: 0 };

    try {
        const res = await fetchPosts(page, category);
        posts = res.data;
        pagination = res.pagination;
    } catch { /* API unavailable */ }

    return (
        <div className="pt-24 pb-16">
            <div className="max-w-6xl mx-auto px-6">
                <h1 className="text-3xl md:text-4xl font-bold text-slate-900">
                    Blog de Salud
                </h1>
                <p className="mt-3 text-slate-500 text-lg">
                    Artículos sobre medicina, ecografía y bienestar familiar.
                </p>

                {posts.length > 0 ? (
                    <>
                        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {posts.map((post) => (
                                <BlogCard key={post.id} post={post} />
                            ))}
                        </div>

                        {/* Pagination */}
                        {pagination.pages > 1 && (
                            <div className="mt-12 flex justify-center gap-2">
                                {Array.from({ length: pagination.pages }, (_, i) => i + 1).map((p) => (
                                    <Link
                                        key={p}
                                        href={`/blog?page=${p}${category ? `&category=${category}` : ""}`}
                                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${p === pagination.page
                                                ? "bg-indigo-600 text-white"
                                                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                                            }`}
                                    >
                                        {p}
                                    </Link>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <div className="mt-16 text-center text-slate-400">
                        <p className="text-lg">No hay artículos publicados aún.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
