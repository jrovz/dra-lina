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
from .schemas import ResearchResult, SeoMetadataSchema
from .research_graph import research_app

load_dotenv()

# --- MODEL CONFIG ---
# Usamos un valor por defecto para el modelo de texto, pero permitimos override
DEFAULT_TEXT_MODEL = "gemini-2.0-flash"


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
        # Ejecutamos el grafo
        inputs = {"topic": topic}
        
        # Invocamos el agente
        # Nota: El agente internamente usa get_llm, que lee el modelo por defecto.
        # Si queremos pasar el modelo dinámicamente, deberíamos pasarlo en el state 
        # o configurar el grafo para aceptarlo. Por ahora usamos la config del grafo.
        
        result = research_app.invoke(inputs)
        
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


def generate_blog_draft(topic: str, tone: str = "profesional y empático", model: str = DEFAULT_TEXT_MODEL) -> str:
    """
    Genera un borrador completo de blog usando LangChain.
    """
    llm = get_llm(model_name=model)
    
    template = """
    Eres la Dra. Lina, una reconocida especialista en salud familiar.
    Escribe un artículo de blog completo sobre: "{topic}"
    
    Requisitos:
    - Extensión: 800-1200 palabras
    - Tono: {tone}. El texto debe ser fácil de leer, entretenido y fluido.
    - Enfoque: Trata temas de salud general y familiar.
    - Formato: HTML con etiquetas <h2>, <h3>, <p>, <ul>, <li>
    - Incluir una introducción muy atractiva (hook).
    - Desarrollar 3-4 secciones principales con subtítulos.
    - Incluir consejos prácticos y aplicables.
    - Terminar con una conclusión memorable y un llamado a la acción.
    - Optimizado para SEO y experiencia de usuario.
    
    NO incluir etiquetas <html>, <head>, <body> ni <h1>.
    Start directly with the content.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    
    try:
        response = chain.invoke({"topic": topic, "tone": tone})
        return response.content
    except Exception as e:
        return f"<p>Error al generar contenido: {str(e)}</p>"


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
                model=model if "flash" in model else "gemini-2.0-flash",
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
            # OpenAI DALL-E 3
            # Podemos usar langchain_community.utilities.dalle_image_generator.DallEAPIWrapper
            # o mantener 'openai' directo. Mantendremos openai directo para no depender de langchain_community por ahora
            # si solo tenemos langchain-openai.
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt_text,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url

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
