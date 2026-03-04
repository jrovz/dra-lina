import Link from "next/link";
import type { BlogPostListItem } from "@/lib/types";
import { format } from "date-fns";
import { es } from "date-fns/locale";

export default function BlogCard({ post }: { post: BlogPostListItem }) {
    const slug = post.slug || String(post.id);
    const date = post.created_at
        ? format(new Date(post.created_at), "d 'de' MMMM, yyyy", { locale: es })
        : "";

    return (
        <Link href={`/blog/${slug}`} className="group">
            <article className="bg-white rounded-2xl border border-slate-100 overflow-hidden hover:shadow-xl hover:shadow-indigo-500/5 hover:-translate-y-1 transition-all duration-300">
                {post.featured_image_url && (
                    <div className="aspect-video bg-slate-100 overflow-hidden">
                        <img
                            src={post.featured_image_url}
                            alt={post.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                    </div>
                )}
                <div className="p-5">
                    {post.category && (
                        <span className="inline-block px-3 py-0.5 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold uppercase tracking-wide">
                            {post.category}
                        </span>
                    )}
                    <h3 className="mt-2 text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                        {post.title}
                    </h3>
                    {date && (
                        <p className="mt-2 text-xs text-slate-400">{date}</p>
                    )}
                </div>
            </article>
        </Link>
    );
}
