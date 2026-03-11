import { fetchPostBySlug } from "@/lib/api";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { format } from "date-fns";
import { es } from "date-fns/locale";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { slug } = await params;
    try {
        const { data: post } = await fetchPostBySlug(slug);
        return {
            title: post.title,
            description: post.seo_keywords || post.title,
            openGraph: {
                title: post.title,
                images: post.featured_image_url ? [post.featured_image_url] : [],
                type: "article",
            },
        };
    } catch {
        return { title: "Post no encontrado" };
    }
}

export default async function PostPage({ params }: Props) {
    const { slug } = await params;
    let post;

    try {
        const res = await fetchPostBySlug(slug);
        post = res.data;
    } catch {
        notFound();
    }

    if (!post) notFound();

    const date = post.created_at
        ? format(new Date(post.created_at), "d 'de' MMMM, yyyy", { locale: es })
        : "";

    return (
        <div className="pt-24 pb-16">
            <article className="max-w-3xl mx-auto px-6">
                {post.category && (
                    <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-semibold uppercase tracking-wide">
                        {post.category}
                    </span>
                )}
                <h1 className="mt-4 text-3xl md:text-4xl font-extrabold text-slate-900 leading-tight">
                    {post.title}
                </h1>
                {date && (
                    <p className="mt-3 text-sm text-slate-400">{date}</p>
                )}

                {post.featured_image_url && (
                    <div className="mt-8 aspect-video rounded-2xl overflow-hidden">
                        <img
                            src={post.featured_image_url}
                            alt={post.title}
                            className="w-full h-full object-cover"
                        />
                    </div>
                )}

                <div
                    className="mt-12 prose prose-slate prose-base md:prose-lg max-w-none break-words overflow-hidden
                    prose-headings:font-extrabold prose-headings:tracking-tight prose-h2:text-indigo-900 prose-h3:text-indigo-800
                    prose-a:text-indigo-600 prose-a:decoration-indigo-300 hover:prose-a:decoration-indigo-600 prose-a:underline-offset-4 prose-a:transition-colors
                    prose-img:rounded-2xl prose-img:shadow-xl prose-img:border prose-img:border-slate-100
                    prose-blockquote:border-l-indigo-500 prose-blockquote:bg-indigo-50 prose-blockquote:px-6 prose-blockquote:py-2 prose-blockquote:rounded-r-xl prose-blockquote:not-italic prose-blockquote:font-medium prose-blockquote:text-indigo-900
                    prose-li:marker:text-indigo-500"
                    dangerouslySetInnerHTML={{ __html: post.content }}
                />

                {post.references && (
                    <div className="mt-10 pt-6 border-t border-slate-200">
                        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                            Referencias
                        </h3>
                        <div className="mt-2 text-sm text-slate-500 whitespace-pre-line">
                            {post.references}
                        </div>
                    </div>
                )}
            </article>
        </div>
    );
}
