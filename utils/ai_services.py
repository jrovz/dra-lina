"""
Servicios de IA para generación de contenido de blog.
Refactorizado para usar LangChain y LangGraph.
"""
import os
import json
import re
from typing import List
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .llm_config import get_llm
from .schemas import ResearchResult, SeoMetadataSchema, BlogDraftSchema
from .research_graph import research_app

load_dotenv()

# --- MODEL CONFIG ---
# Usamos un valor por defecto para el modelo de texto, pero permitimos override
DEFAULT_TEXT_MODEL = "gpt-5.2"


# --- FUNCIONES REFACTORIZADAS ---

def research_topic(topic: str, model: str = DEFAULT_TEXT_MODEL) -> dict:
    """
    Investiga un tema usando el Agente de Investigación Profunda (LangGraph).
    
    Args:
        topic: El tema a investigar
        model: El modelo de IA a usar (se pasa el nombre al grafo)
        
    Returns:
        dict con puntos_clave, preguntas_frecuentes, keywords_seo
    """
    try:
        inputs = {"topic": topic}
        config = {"configurable": {"model": model}}
        result = research_app.invoke(inputs, config=config)
        
        # El resultado final está en el estado 'final_report'
        if "final_report" in result and result["final_report"]:
            return result["final_report"]
        else:
            return _fallback_research(topic, model)

    except Exception as e:
        print(f"Error en LangGraph research: {e}")
        return _fallback_research(topic, model)


def _fallback_research(topic: str, model: str) -> dict:
    """Fallback usando una cadena simple si el grafo falla."""
    print("Usando fallback research...")
    llm = get_llm(model_name=model)
    structured_llm = llm.with_structured_output(ResearchResult)
    
    prompt = f"Investiga el tema: '{topic}'. Actúa como experta en salud familiar."
    
    try:
        result = structured_llm.invoke(prompt)
        return result.dict()
    except Exception as e:
         return {
            "puntos_clave": [f"Error al procesar la investigación: {str(e)}"],
            "preguntas_frecuentes": [],
            "keywords_seo": []
        }


def generate_blog_draft(topic: str, tone: str = "profesional y empático", 
                        model: str = DEFAULT_TEXT_MODEL,
                        research: dict = None) -> dict:
    """
    Genera un borrador de blog estructurado usando LangChain con salida estructurada.
    Si se proporciona `research`, usa los puntos clave y referencias de la investigación.
    Retorna un dict con 'title' y 'blocks' (lista de ContentBlock).
    """
    llm = get_llm(model_name=model)
    structured_llm = llm.with_structured_output(BlogDraftSchema)
    
    # Construir contexto de investigación si está disponible
    research_context = ""
    references_section = ""
    
    if research and isinstance(research, dict):
        # Puntos clave (lista de strings)
        puntos = research.get('puntos_clave', [])
        if puntos and isinstance(puntos, list):
            research_context += "\n\nPuntos clave de la investigación:\n"
            research_context += "\n".join(f"- {p}" for p in puntos if isinstance(p, str))
        
        # Preguntas frecuentes (puede ser lista de strings o de objetos)
        faqs = research.get('preguntas_frecuentes', [])
        if faqs and isinstance(faqs, list):
            research_context += "\n\nPreguntas frecuentes a responder:\n"
            for q in faqs:
                if isinstance(q, str):
                    research_context += f"- {q}\n"
                elif isinstance(q, dict):
                    research_context += f"- {q.get('pregunta', q.get('question', str(q)))}\n"
        
        # Referencias (puede ser lista de dicts o de strings)
        refs = research.get('references', [])
        if refs and isinstance(refs, list):
            references_section = "\n\nFuentes consultadas (incluirlas al final):\n"
            for ref in refs[:5]:
                if isinstance(ref, dict):
                    references_section += f"- {ref.get('title', 'Sin título')}"
                    if ref.get('url'):
                        references_section += f" ({ref['url']})"
                    references_section += "\n"
                elif isinstance(ref, str):
                    references_section += f"- {ref}\n"
    
    prompt = f"""
    Eres la Dra. Lina, una reconocida especialista en salud familiar.
    Genera un artículo de blog completo sobre: "{topic}"
    {research_context}
    
    Requisitos:
    - Extensión: 800-1200 palabras (distribuidas en bloques)
    - Tono: {tone}. El texto debe ser fácil de leer, entretenido y fluido.
    - Enfoque: Trata temas de salud general y familiar.
    - Incluir una introducción atractiva (primer bloque: paragraph).
    - Desarrollar 3-4 secciones principales (heading + paragraphs).
    - Responder las preguntas frecuentes si están disponibles.
    - Incluir consejos prácticos (list blocks).
    - Terminar con una conclusión memorable.
    - Optimizado para SEO.
    {references_section}
    
    IMPORTANTE: Si hay fuentes consultadas, incluir al final una sección "Referencias" (heading) 
    con una lista (list block) de las fuentes con sus URLs.
    
    Estructura el contenido en bloques con tipos: heading, subheading, paragraph, list, quote.
    Para listas, usa saltos de línea para separar items.
    """
    
    try:
        result = structured_llm.invoke(prompt)
        return result.model_dump()
    except Exception as e:
        return {
            "title": topic,
            "blocks": [{"type": "paragraph", "content": f"Error al generar contenido: {str(e)}"}]
        }


def generate_seo_metadata(title: str, content: str) -> dict:
    """
    Genera metadatos SEO usando StructuredOutput de LangChain.
    """
    # Truncar contenido para el prompt
    content_preview = content[:2000] if len(content) > 2000 else content
    
    llm = get_llm(model_name=DEFAULT_TEXT_MODEL)
    structured_llm = llm.with_structured_output(SeoMetadataSchema)
    
    prompt = f"""
    Genera metadatos SEO para este artículo:
    Título: {title}
    Contenido (preview): {content_preview}
    """
    
    try:
        result = structured_llm.invoke(prompt)
        return result.dict()
    except Exception as e:
        return {
            "meta_description": "",
            "keywords": [],
            "slug_sugerido": ""
        }


def refine_block_content(content: str, action: str, context: str = "", model: str = DEFAULT_TEXT_MODEL) -> str:
    """
    Refina el contenido usando LangChain.
    """
    llm = get_llm(model_name=model)
    
    action_prompts = {
        "expand": "Expande este párrafo con más detalles (2-3 párrafos extra).",
        "shorten": "Resume este texto en 1-2 oraciones claras.",
        "formal": "Reescribe con un tono formal y médico profesional.",
        "casual": "Reescribe con un tono cercano y fácil de entender.",
        "scientific": "Añade enfoque científico y datos precisos."
    }
    
    instruction = action_prompts.get(action, "Mejora este texto.")
    
    template = """
    Eres la Dra. Lina.
    Contexto: {context}
    
    Texto original:
    "{content}"
    
    Instrucción: {instruction}
    Devuelve SOLO el texto reescrito.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "content": content, 
            "context": context, 
            "instruction": instruction
        })
        return response.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def generate_featured_image(title: str, model: str = "dall-e-3") -> str:
    """
    Genera imagen. Mantenemos la lógica original pero usamos los clientes centralizados donde sea posible.
    Para DALL-E, LangChain tiene wrapper pero para generación de imagen directa a veces es mejor la API directa si devuelve URL.
    LangChain 'DallEAPIWrapper' existe, pero para mantener consistencia con el código anterior de guardado local (Gemini) 
    vs URL (DALL-E), adaptaremos ligeramente.
    """
    
    prompt_text = f"""
    Imagen profesional y cálida para un artículo médico sobre: "{title}".
    Estilo: Fotografía editorial suave, iluminación natural y colores cálidos.
    Tema: Salud familiar integral, crianza, bienestar.
    Sin texto. Sin rostros definidos.
    """
    
    try:
        if "gemini" in model.lower():
            # Usamos el cliente de Gemini via Google GenAI SDK directo porque LangChain ChatGoogleGenerativeAI 
            # está enfocado en chat/texto, aunque soporta multimodal input, output de imagen es diferente.
            # Podríamos instanciar el cliente aquí o exponerlo en llm_config. Importaremos directo por compatibilidad.
            from google import genai
            
            api_key = os.environ.get("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            
            response = client.models.generate_content(
                model=model if "flash" in model else "gemini-3-flash",
                contents=prompt_text,
                config={'response_mime_type': 'image/png'}
            )
            
            # Procesar imagen (lógica original)
            image_data = None
            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        image_data = part.inline_data.data
                        break
                        
            if not image_data:
                return "error: No se recibió imagen de Gemini."

            # Guardar
            import uuid
            from datetime import datetime
            
            filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
            save_path = os.path.join("static", "generated_images", filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, "wb") as f:
                f.write(image_data)
                
            return f"/static/generated_images/{filename}"

        else:
            # OpenAI DALL-E 3 - Ahora descargamos y guardamos localmente para consistencia
            import uuid
            import requests
            from datetime import datetime
            from openai import OpenAI
            
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt_text,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            
            # Descargar imagen y guardar localmente
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code == 200:
                filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
                save_path = os.path.join("static", "generated_images", filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(img_response.content)
                    
                return f"/static/generated_images/{filename}"
            else:
                return f"error: No se pudo descargar la imagen de DALL-E"

    except Exception as e:
        return f"error:{str(e)}"


def analyze_seo(title: str, content: str, keywords: list) -> dict:
    """
    Mantenemos la lógica original de análisis SEO por ahora, ya que es determinista y rápida.
    Podríamos moverla a un agente 'Reviewer' en el futuro.
    """
    # ... (Copiar lógica original o importarla si la separamos)
    # Para simplicidad, pego la lógica original de conteo de palabras
    
    clean_content = re.sub(r'<[^>]+>', ' ', content).lower()
    word_count = len(clean_content.split())
    
    issues = []
    score = 100
    
    if word_count < 300:
        issues.append("⚠️ Contenido muy corto (< 300 palabras)")
        score -= 20
    elif word_count < 600:
        issues.append("💡 Considera expandir a 600+ palabras")
        score -= 10
    
    if len(title) < 30:
        issues.append("⚠️ Título muy corto")
        score -= 10
    
    keyword_presence = {}
    for kw in keywords[:5]:
        kw_lower = kw.lower()
        count = clean_content.count(kw_lower)
        keyword_presence[kw] = count
        if count == 0:
            issues.append(f"❌ Keyword '{kw}' no encontrada")
            score -= 10
    
    return {
        "score": max(0, score),
        "issues": issues,
        "word_count": word_count,
        "keyword_presence": keyword_presence
    }
