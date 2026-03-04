"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
    createPost, updatePost, aiResearch, aiGenerateDraft,
    aiGenerateImage, aiRefineBlock, aiSeoAnalyze, ApiError
} from "@/lib/api";

// ============ TYPES ============

type BlockType = "paragraph" | "heading" | "subheading" | "image" | "list" | "quote";

interface Block {
    id: string;
    type: BlockType;
    content: string;
    imageUrl?: string;
    caption?: string;
}

interface ResearchData {
    puntos_clave?: string[];
    preguntas_frecuentes?: string[];
    keywords_seo?: string[];
    references?: { title: string; url?: string; snippet?: string }[];
}

interface SeoResult {
    score: number;
    word_count: number;
    issues: string[];
    keyword_presence?: Record<string, number>;
}

const AI_MODELS = [
    {
        group: "OpenAI", options: [
            { value: "gpt-5.2", label: "GPT-5.2 (Best)" },
            { value: "gpt-5-mini", label: "GPT-5 Mini" },
        ]
    },
    {
        group: "Google Gemini", options: [
            { value: "gemini-3-pro", label: "Gemini 3 Pro" },
            { value: "gemini-3-flash", label: "Gemini 3 Flash" },
        ]
    },
];

const BLOCK_TYPES: { type: BlockType; icon: string; label: string }[] = [
    { type: "paragraph", icon: "📝", label: "Párrafo" },
    { type: "heading", icon: "📌", label: "Título (H2)" },
    { type: "subheading", icon: "📎", label: "Subtítulo (H3)" },
    { type: "image", icon: "🖼️", label: "Imagen" },
    { type: "list", icon: "📋", label: "Lista" },
    { type: "quote", icon: "💬", label: "Cita" },
];

const AI_BLOCK_ACTIONS = [
    { action: "expand", icon: "✨", label: "Expandir" },
    { action: "shorten", icon: "📝", label: "Resumir" },
    { action: "formal", icon: "🎩", label: "Tono Formal" },
    { action: "casual", icon: "💬", label: "Tono Casual" },
    { action: "scientific", icon: "🔬", label: "Científico" },
];

let blockCounter = 0;
function newBlockId() { return `block-${blockCounter++}`; }

// ============ MAIN COMPONENT ============

export default function PostEditorPage() {
    const router = useRouter();
    const params = useParams();
    const isNew = params.id === "new";
    const queryClient = useQueryClient();

    // Form state
    const [title, setTitle] = useState("");
    const [prompt, setPrompt] = useState("");
    const [model, setModel] = useState("gpt-5.2");
    const [blocks, setBlocks] = useState<Block[]>([{ id: newBlockId(), type: "paragraph", content: "" }]);
    const [featuredImage, setFeaturedImage] = useState("");
    const [isPublished, setIsPublished] = useState(true);
    const [category, setCategory] = useState("");
    const [seoKeywordsInput, setSeoKeywordsInput] = useState("");

    // AI state
    const [loading, setLoading] = useState(false);
    const [loadingText, setLoadingText] = useState("");
    const [researchData, setResearchData] = useState<ResearchData | null>(null);
    const [seoResult, setSeoResult] = useState<SeoResult | null>(null);
    const [showResearch, setShowResearch] = useState(false);
    const [showSeo, setShowSeo] = useState(false);
    const [showBlockMenu, setShowBlockMenu] = useState(false);
    const [aiMenuBlockId, setAiMenuBlockId] = useState<string | null>(null);
    const [aiMenuPos, setAiMenuPos] = useState({ top: 0, left: 0 });

    // Drag state
    const draggedRef = useRef<string | null>(null);

    // Serialization
    const serializeToHTML = useCallback(() => {
        return blocks.map((b) => {
            switch (b.type) {
                case "paragraph":
                    return b.content.trim() ? `<p>${b.content.replace(/\n/g, "<br>")}</p>` : "";
                case "heading":
                    return b.content.trim() ? `<h2>${b.content}</h2>` : "";
                case "subheading":
                    return b.content.trim() ? `<h3>${b.content}</h3>` : "";
                case "image":
                    const url = b.imageUrl || b.content;
                    const alt = b.caption || "Imagen";
                    return url ? `<figure><img src="${url}" alt="${alt}"><figcaption>${alt}</figcaption></figure>` : "";
                case "list":
                    if (!b.content.trim()) return "";
                    const items = b.content.split("\n").filter(i => i.trim()).map(i => `  <li>${i.replace(/^[-•*]\s*/, "").trim()}</li>`).join("\n");
                    return `<ul>\n${items}\n</ul>`;
                case "quote":
                    return b.content.trim() ? `<blockquote>${b.content}</blockquote>` : "";
                default: return "";
            }
        }).filter(Boolean).join("\n");
    }, [blocks]);

    // ============ BLOCK OPERATIONS ============

    function addBlock(type: BlockType) {
        setBlocks(prev => [...prev, { id: newBlockId(), type, content: "" }]);
        setShowBlockMenu(false);
    }

    function updateBlock(id: string, updates: Partial<Block>) {
        setBlocks(prev => prev.map(b => b.id === id ? { ...b, ...updates } : b));
    }

    function deleteBlock(id: string) {
        if (!confirm("¿Eliminar este bloque?")) return;
        setBlocks(prev => prev.filter(b => b.id !== id));
    }

    function insertBlockAt(type: BlockType, content: string, position?: number) {
        const newBlock: Block = { id: newBlockId(), type, content };
        setBlocks(prev => {
            if (position !== undefined) {
                const copy = [...prev];
                copy.splice(position, 0, newBlock);
                return copy;
            }
            return [...prev, newBlock];
        });
    }

    // ============ DRAG & DROP ============

    function handleDragStart(blockId: string) { draggedRef.current = blockId; }
    function handleDragEnd() { draggedRef.current = null; }
    function handleDrop(targetId: string) {
        if (!draggedRef.current || draggedRef.current === targetId) return;
        setBlocks(prev => {
            const copy = [...prev];
            const dragIdx = copy.findIndex(b => b.id === draggedRef.current);
            const targetIdx = copy.findIndex(b => b.id === targetId);
            const [dragged] = copy.splice(dragIdx, 1);
            copy.splice(targetIdx, 0, dragged);
            return copy;
        });
        draggedRef.current = null;
    }

    // ============ AI FEATURES ============

    async function handleResearch() {
        const topic = title || prompt;
        if (!topic) { alert("Ingresa un título o un prompt primero"); return; }
        if (!title && prompt) setTitle(prompt);

        setLoading(true); setLoadingText("Investigando tema...");
        try {
            const res = await aiResearch(topic, model);
            const research = res.research as ResearchData;
            setResearchData(research);
            if (research.keywords_seo) setSeoKeywordsInput(research.keywords_seo.join(", "));
            setShowResearch(true);
        } catch (err) {
            alert(err instanceof ApiError ? err.message : "Error en investigación");
        } finally { setLoading(false); }
    }

    async function handleDraft() {
        const topic = title || prompt;
        if (!topic) { alert("Ingresa un título o un prompt primero"); return; }
        if (blocks.some(b => b.content.trim()) && !confirm("Esto reemplazará los bloques actuales. ¿Continuar?")) return;

        setLoading(true); setLoadingText("Generando borrador con IA...");
        try {
            const res = await aiGenerateDraft(topic, model, researchData || undefined);
            const draft = res.content as { title?: string; blocks?: { type: string; content: string }[] };

            if (draft.title) setTitle(draft.title);

            if (draft.blocks?.length) {
                const newBlocks: Block[] = draft.blocks.map(b => ({
                    id: newBlockId(),
                    type: (["heading", "subheading", "paragraph", "list", "quote", "image"].includes(b.type) ? b.type : "paragraph") as BlockType,
                    content: b.type === "list"
                        ? b.content.split("\n").map(i => i.startsWith("- ") ? i : "- " + i).join("\n")
                        : b.content,
                }));
                setBlocks(newBlocks);
            }
        } catch (err) {
            alert(err instanceof ApiError ? err.message : "Error generando borrador");
        } finally { setLoading(false); }
    }

    async function handleImage() {
        const imgTitle = title || prompt;
        if (!imgTitle) { alert("Ingresa un título o un prompt primero"); return; }

        setLoading(true); setLoadingText("Generando imagen con DALL-E...");
        try {
            const res = await aiGenerateImage(imgTitle, model);
            insertBlockAt("image", "", undefined);
            setBlocks(prev => {
                const copy = [...prev];
                copy[copy.length - 1].imageUrl = res.image_url;
                return copy;
            });
            if (!featuredImage) setFeaturedImage(res.image_url);
        } catch (err) {
            alert(err instanceof ApiError ? err.message : "Error generando imagen");
        } finally { setLoading(false); }
    }

    async function handleSeo() {
        const content = serializeToHTML();
        if (!title || !content) { alert("Necesitas un título y contenido para analizar SEO"); return; }

        setLoading(true); setLoadingText("Analizando SEO...");
        try {
            const res = await aiSeoAnalyze(title, content, seoKeywordsInput.split(",").map(k => k.trim()).filter(Boolean));
            setSeoResult(res as SeoResult);
            setShowSeo(true);
        } catch (err) {
            alert(err instanceof ApiError ? err.message : "Error en análisis SEO");
        } finally { setLoading(false); }
    }

    async function handleBlockAiAction(action: string) {
        if (!aiMenuBlockId) return;
        const block = blocks.find(b => b.id === aiMenuBlockId);
        if (!block || !block.content.trim()) { alert("El bloque está vacío"); setAiMenuBlockId(null); return; }

        setAiMenuBlockId(null);
        setLoading(true); setLoadingText(`Procesando: ${action}...`);
        try {
            const res = await aiRefineBlock(block.content, action, title, model);
            updateBlock(block.id, { content: res.refined_content });
        } catch (err) {
            alert(err instanceof ApiError ? err.message : "Error procesando bloque");
        } finally { setLoading(false); }
    }

    async function handleInlineImageGenerate(blockId: string) {
        const block = blocks.find(b => b.id === blockId);
        const caption = block?.caption || title || "Imagen médica";

        setLoading(true); setLoadingText("Generando imagen con DALL-E 3...");
        try {
            const res = await aiGenerateImage(caption);
            updateBlock(blockId, { imageUrl: res.image_url });
        } catch (err) {
            alert(err instanceof ApiError ? err.message : "Error generando imagen");
        } finally { setLoading(false); }
    }

    // ============ SAVE ============

    const saveMutation = useMutation({
        mutationFn: () => {
            const html = serializeToHTML();
            if (!html.trim()) throw new Error("Añade al menos un bloque de contenido");
            const payload = {
                title, content: html, featured_image_url: featuredImage,
                seo_keywords: seoKeywordsInput, category, is_published: isPublished,
                references: researchData?.references ? JSON.stringify(researchData.references) : "",
            };
            return isNew ? createPost(payload) : updatePost(Number(params.id), payload);
        },
        onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["admin-posts"] }); router.push("/posts"); },
        onError: (err) => alert(err.message),
    });

    // Close menus on outside click
    useEffect(() => {
        function handler(e: MouseEvent) {
            if (!(e.target as HTMLElement).closest(".ai-action-menu-react")) setAiMenuBlockId(null);
        }
        document.addEventListener("click", handler);
        return () => document.removeEventListener("click", handler);
    }, []);

    // ============ RENDER ============

    return (
        <div className="max-w-[1400px] mx-auto flex gap-6">
            {/* Main Editor */}
            <div className="flex-1 min-w-0">
                {/* Header */}
                <header className="text-center mb-6">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
                        🧠 AI Content Studio
                    </h1>
                    <p className="text-sm text-slate-500 mt-1">Editor visual por bloques con asistencia de IA</p>
                </header>

                {/* Loading */}
                {loading && (
                    <div className="flex items-center gap-3 justify-center py-4 bg-indigo-50 rounded-xl mb-4">
                        <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                        <span className="text-sm text-indigo-700 font-medium">{loadingText}</span>
                    </div>
                )}

                {/* Chat-style Prompt */}
                <div className="bg-gradient-to-br from-indigo-50/80 to-violet-50/80 border-2 border-indigo-200/50 rounded-2xl p-4 mb-6">
                    <div className="flex items-center gap-2 mb-3">
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="Describe el artículo que deseas generar..."
                            rows={1}
                            className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none resize-none"
                            onInput={(e) => { const t = e.target as HTMLTextAreaElement; t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight, 150) + "px"; }}
                        />
                    </div>

                    <div className="flex items-center justify-between gap-3 flex-wrap">
                        <div className="flex gap-2">
                            <button onClick={handleResearch} disabled={loading}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-sm font-medium hover:bg-slate-50 disabled:opacity-40 transition-colors">
                                <span>🔍</span> Investigar
                            </button>
                            <button onClick={handleDraft} disabled={loading}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 transition-colors">
                                <span>✍️</span> Generar Borrador
                            </button>
                            <button onClick={handleImage} disabled={loading}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-sm font-medium hover:bg-slate-50 disabled:opacity-40 transition-colors">
                                <span>🎨</span> Imagen
                            </button>
                            <button onClick={handleSeo} disabled={loading}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-emerald-200 text-sm font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-40 transition-colors">
                                <span>📊</span> SEO
                            </button>
                        </div>

                        {/* Model selector */}
                        <select value={model} onChange={(e) => setModel(e.target.value)}
                            className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:border-indigo-500 outline-none">
                            {AI_MODELS.map((g) => (
                                <optgroup key={g.group} label={g.group}>
                                    {g.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                                </optgroup>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Research Panel */}
                {showResearch && researchData && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-5 mb-6">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-bold text-slate-900">📊 Investigación</h3>
                            <button onClick={() => setShowResearch(false)} className="text-slate-400 hover:text-slate-600 text-xl">×</button>
                        </div>
                        <div className="space-y-4 text-sm">
                            {researchData.puntos_clave?.length ? (
                                <div>
                                    <h4 className="font-semibold text-indigo-700 mb-2">💡 Puntos Clave</h4>
                                    <ul className="space-y-1.5">
                                        {researchData.puntos_clave.map((p, i) => (
                                            <li key={i} className="flex items-start gap-2">
                                                <span className="flex-1 text-slate-600">{p}</span>
                                                <button onClick={() => insertBlockAt("heading", p)} className="text-xs px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700 hover:bg-indigo-200 shrink-0">+H2</button>
                                                <button onClick={() => insertBlockAt("paragraph", p)} className="text-xs px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 hover:bg-slate-200 shrink-0">+P</button>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ) : null}

                            {researchData.preguntas_frecuentes?.length ? (
                                <div>
                                    <h4 className="font-semibold text-amber-700 mb-2">❓ Preguntas Frecuentes</h4>
                                    <ul className="space-y-1.5">
                                        {researchData.preguntas_frecuentes.map((q, i) => (
                                            <li key={i} className="flex items-start gap-2">
                                                <span className="flex-1 text-slate-600">{q}</span>
                                                <button onClick={() => insertBlockAt("subheading", q)} className="text-xs px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 hover:bg-amber-200 shrink-0">+H3</button>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ) : null}

                            {researchData.keywords_seo?.length ? (
                                <div>
                                    <h4 className="font-semibold text-emerald-700 mb-2">🔑 Keywords SEO</h4>
                                    <div className="flex flex-wrap gap-1.5">
                                        {researchData.keywords_seo.map((k, i) => (
                                            <span key={i} className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-medium">{k}</span>
                                        ))}
                                    </div>
                                </div>
                            ) : null}

                            {researchData.references?.length ? (
                                <div>
                                    <h4 className="font-semibold text-violet-700 mb-2">📚 Referencias</h4>
                                    <ul className="space-y-2">
                                        {researchData.references.map((ref, i) => (
                                            <li key={i} className="text-slate-600">
                                                <strong>{ref.title}</strong>
                                                {ref.url && <a href={ref.url} target="_blank" rel="noopener" className="ml-1 text-indigo-600">🔗</a>}
                                                {ref.snippet && <p className="text-xs text-slate-400 mt-0.5">{ref.snippet}</p>}
                                            </li>
                                        ))}
                                    </ul>
                                    <button onClick={() => {
                                        insertBlockAt("heading", "Referencias");
                                        const refsContent = researchData.references!.map(r => r.url ? `${r.title} - ${r.url}` : r.title).join("\n");
                                        setTimeout(() => insertBlockAt("list", refsContent), 0);
                                    }} className="mt-2 text-xs px-2 py-1 rounded bg-violet-100 text-violet-700 hover:bg-violet-200">
                                        📚 Insertar Referencias al Blog
                                    </button>
                                </div>
                            ) : null}
                        </div>
                    </div>
                )}

                {/* Title */}
                <div className="mb-4">
                    <input value={title} onChange={(e) => setTitle(e.target.value)}
                        placeholder="Título del artículo"
                        className="w-full px-4 py-3 text-xl font-bold border border-slate-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none bg-white" />
                </div>

                {/* Block Editor */}
                <div className="space-y-3 mb-6">
                    {blocks.map((block) => (
                        <div key={block.id}
                            draggable
                            onDragStart={() => handleDragStart(block.id)}
                            onDragEnd={handleDragEnd}
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={() => handleDrop(block.id)}
                            className="group bg-white border border-slate-200 rounded-xl p-3 hover:border-indigo-300 transition-colors"
                        >
                            <div className="flex items-start gap-2">
                                {/* Drag handle */}
                                <div className="cursor-grab text-slate-300 hover:text-slate-500 pt-1 select-none" title="Arrastra para reordenar">⋮⋮</div>

                                {/* Content */}
                                <div className="flex-1 min-w-0">
                                    {block.type === "paragraph" && (
                                        <textarea value={block.content} onChange={(e) => updateBlock(block.id, { content: e.target.value })}
                                            placeholder="Escribe tu párrafo aquí..." rows={3}
                                            className="w-full border-0 outline-none text-sm resize-none leading-relaxed" />
                                    )}
                                    {block.type === "heading" && (
                                        <input value={block.content} onChange={(e) => updateBlock(block.id, { content: e.target.value })}
                                            placeholder="Título de sección (H2)"
                                            className="w-full border-0 outline-none text-lg font-bold" />
                                    )}
                                    {block.type === "subheading" && (
                                        <input value={block.content} onChange={(e) => updateBlock(block.id, { content: e.target.value })}
                                            placeholder="Subtítulo (H3)"
                                            className="w-full border-0 outline-none text-base font-semibold text-slate-700" />
                                    )}
                                    {block.type === "image" && (
                                        <div className="space-y-2">
                                            {block.imageUrl && <img src={block.imageUrl} alt={block.caption || "Preview"} className="rounded-lg max-h-48 object-cover" />}
                                            <input value={block.imageUrl || ""} onChange={(e) => updateBlock(block.id, { imageUrl: e.target.value })}
                                                placeholder="URL de imagen" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-indigo-500" />
                                            <input value={block.caption || ""} onChange={(e) => updateBlock(block.id, { caption: e.target.value })}
                                                placeholder="Descripción (alt text)" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-indigo-500" />
                                            <button onClick={() => handleInlineImageGenerate(block.id)} disabled={loading}
                                                className="text-xs px-3 py-1.5 rounded-lg bg-violet-100 text-violet-700 hover:bg-violet-200 disabled:opacity-40">
                                                🎨 Generar con IA
                                            </button>
                                        </div>
                                    )}
                                    {block.type === "list" && (
                                        <textarea value={block.content} onChange={(e) => updateBlock(block.id, { content: e.target.value })}
                                            placeholder={"Escribe cada item en una línea:\n- Item 1\n- Item 2"} rows={4}
                                            className="w-full border-0 outline-none text-sm resize-none font-mono" />
                                    )}
                                    {block.type === "quote" && (
                                        <textarea value={block.content} onChange={(e) => updateBlock(block.id, { content: e.target.value })}
                                            placeholder="Escribe una cita destacada..." rows={2}
                                            className="w-full border-0 outline-none text-sm italic text-slate-600 border-l-4 border-indigo-300 pl-3 resize-none" />
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity pt-1">
                                    {["paragraph", "list", "quote"].includes(block.type) && (
                                        <button onClick={(e) => {
                                            e.stopPropagation();
                                            const rect = (e.target as HTMLElement).getBoundingClientRect();
                                            setAiMenuPos({ top: rect.bottom + 5, left: rect.left });
                                            setAiMenuBlockId(block.id);
                                        }} className="p-1 rounded hover:bg-indigo-50 text-sm ai-action-menu-react" title="Acciones IA">✨</button>
                                    )}
                                    <button onClick={() => deleteBlock(block.id)} className="p-1 rounded hover:bg-red-50 text-sm" title="Eliminar">🗑️</button>
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Add Block */}
                    <div className="relative">
                        <button onClick={() => setShowBlockMenu(!showBlockMenu)}
                            className="w-full py-3 border-2 border-dashed border-slate-200 rounded-xl text-slate-400 hover:border-indigo-300 hover:text-indigo-500 transition-colors font-medium text-sm">
                            + Añadir Bloque
                        </button>
                        {showBlockMenu && (
                            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-lg p-2 z-10 grid grid-cols-3 gap-1">
                                {BLOCK_TYPES.map((bt) => (
                                    <button key={bt.type} onClick={() => addBlock(bt.type)}
                                        className="px-3 py-2 rounded-lg text-sm font-medium hover:bg-indigo-50 text-left">
                                        {bt.icon} {bt.label}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Featured Image */}
                {featuredImage && (
                    <div className="mb-6 bg-white border rounded-xl p-4">
                        <label className="text-xs font-medium text-slate-500 block mb-2">🖼️ Imagen Destacada</label>
                        <img src={featuredImage} alt="Featured" className="rounded-lg max-h-48 object-cover" />
                        <button onClick={() => setFeaturedImage("")} className="mt-2 text-xs text-red-500 hover:text-red-700">Quitar</button>
                    </div>
                )}

                {/* Meta fields */}
                <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6 space-y-3">
                    <div className="flex gap-4">
                        <div className="flex-1">
                            <label className="block text-xs font-medium text-slate-600 mb-1">Categoría</label>
                            <input value={category} onChange={(e) => setCategory(e.target.value)}
                                placeholder="salud, ecografía..." className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm outline-none focus:border-indigo-500" />
                        </div>
                        <div className="flex-1">
                            <label className="block text-xs font-medium text-slate-600 mb-1">Keywords SEO</label>
                            <input value={seoKeywordsInput} onChange={(e) => setSeoKeywordsInput(e.target.value)}
                                placeholder="dermatología, piel..." className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm outline-none focus:border-indigo-500" />
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <input type="checkbox" checked={isPublished} onChange={(e) => setIsPublished(e.target.checked)} className="rounded" id="pub" />
                        <label htmlFor="pub" className="text-sm text-slate-600">Publicar</label>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                    <button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}
                        className="px-6 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors">
                        {saveMutation.isPending ? "Guardando..." : isNew ? "🚀 Publicar" : "💾 Guardar cambios"}
                    </button>
                    <button onClick={() => router.push("/posts")} className="px-6 py-2.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50">
                        Cancelar
                    </button>
                </div>
            </div>

            {/* SEO Sidebar */}
            {showSeo && seoResult && (
                <aside className="w-72 shrink-0">
                    <div className="bg-white border border-slate-200 rounded-2xl p-4 sticky top-24">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-bold text-sm">📊 SEO Score</h3>
                            <button onClick={() => setShowSeo(false)} className="text-slate-400 hover:text-slate-600">×</button>
                        </div>

                        {/* Score Circle */}
                        <div className="flex justify-center mb-4">
                            <svg viewBox="0 0 36 36" className="w-24 h-24">
                                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none" stroke="#e5e7eb" strokeWidth="3" />
                                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    fill="none" strokeWidth="3" strokeLinecap="round"
                                    strokeDasharray={`${seoResult.score}, 100`}
                                    stroke={seoResult.score >= 70 ? "#22c55e" : seoResult.score >= 40 ? "#f59e0b" : "#ef4444"} />
                                <text x="18" y="20.35" textAnchor="middle" className="fill-slate-900 text-[8px] font-bold">
                                    {seoResult.score}
                                </text>
                            </svg>
                        </div>

                        <div className="text-center text-sm text-slate-500 mb-4">{seoResult.word_count} palabras</div>

                        {/* Issues */}
                        <div className="space-y-1.5 mb-4">
                            {seoResult.issues.length > 0 ? (
                                seoResult.issues.map((issue, i) => (
                                    <div key={i} className="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-1.5">{issue}</div>
                                ))
                            ) : (
                                <div className="text-xs text-emerald-700 bg-emerald-50 rounded-lg px-3 py-1.5">✅ ¡Excelente! No hay problemas detectados.</div>
                            )}
                        </div>

                        {/* Keyword Presence */}
                        {seoResult.keyword_presence && Object.keys(seoResult.keyword_presence).length > 0 && (
                            <div>
                                <h4 className="text-xs font-semibold text-slate-700 mb-2">Keywords</h4>
                                <div className="space-y-1">
                                    {Object.entries(seoResult.keyword_presence).map(([kw, count]) => (
                                        <div key={kw} className={`text-xs px-2 py-1 rounded flex justify-between ${count >= 2 ? "bg-emerald-50 text-emerald-700" : count >= 1 ? "bg-amber-50 text-amber-700" : "bg-red-50 text-red-700"
                                            }`}>
                                            <span>{kw}</span>
                                            <span>{count}x</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </aside>
            )}

            {/* Floating AI Action Menu */}
            {aiMenuBlockId && (
                <div className="ai-action-menu-react fixed bg-white border border-slate-200 rounded-xl shadow-xl p-1.5 z-50"
                    style={{ top: aiMenuPos.top, left: aiMenuPos.left }}>
                    {AI_BLOCK_ACTIONS.map(({ action, icon, label }) => (
                        <button key={action} onClick={() => handleBlockAiAction(action)}
                            className="w-full text-left px-3 py-1.5 rounded-lg text-sm hover:bg-indigo-50 flex items-center gap-2">
                            <span>{icon}</span> {label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
