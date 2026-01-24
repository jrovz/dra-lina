"""
Servicios de IA para generación de contenido de blog.
Utiliza Gemini para texto y OpenAI DALL-E 3 para imágenes.
"""
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# --- Configuración de APIs ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Lazy imports para evitar errores si las dependencias no están instaladas
_openai_client = None
_genai_model = None


def _get_openai_client():
    """Obtiene el cliente de OpenAI (lazy loading)."""
    global _openai_client
    if _openai_client is None:
        import openai
        _openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _get_gemini_model():
    """Obtiene el modelo de Gemini (lazy loading)."""
    global _genai_model
    if _genai_model is None:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _genai_model = genai.GenerativeModel("gemini-1.5-flash")
    return _genai_model


def research_topic(topic: str) -> dict:
    """
    Investiga un tema y devuelve puntos clave para el blog.
    
    Args:
        topic: El tema a investigar
        
    Returns:
        dict con puntos_clave, preguntas_frecuentes, keywords_seo
    """
    model = _get_gemini_model()
    
    prompt = f"""
    Eres una ginecóloga experta en salud maternal y embarazo.
    Investiga el tema: "{topic}"
    
    Devuelve ÚNICAMENTE un JSON válido (sin markdown, sin ```json) con esta estructura:
    {{
        "puntos_clave": ["punto 1", "punto 2", "punto 3", "punto 4", "punto 5"],
        "preguntas_frecuentes": ["pregunta 1", "pregunta 2", "pregunta 3"],
        "keywords_seo": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Limpiar posibles marcadores de código
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "puntos_clave": ["Error al procesar la investigación"],
            "preguntas_frecuentes": [],
            "keywords_seo": []
        }
    except Exception as e:
        return {
            "error": str(e),
            "puntos_clave": [],
            "preguntas_frecuentes": [],
            "keywords_seo": []
        }


def generate_blog_draft(topic: str, tone: str = "profesional y empático") -> str:
    """
    Genera un borrador completo de blog usando Gemini.
    
    Args:
        topic: El tema del artículo
        tone: El tono deseado para el contenido
        
    Returns:
        str: Contenido HTML del artículo
    """
    model = _get_gemini_model()
    
    prompt = f"""
    Eres la Dra. Lina, una ginecóloga experta en salud maternal.
    Escribe un artículo de blog completo sobre: "{topic}"
    
    Requisitos:
    - Extensión: 800-1200 palabras
    - Tono: {tone}
    - Formato: HTML con etiquetas <h2>, <h3>, <p>, <ul>, <li>
    - Incluir una introducción atractiva
    - Desarrollar 3-4 secciones principales con subtítulos
    - Incluir consejos prácticos
    - Terminar con una conclusión y llamado a la acción
    - Optimizado para SEO y AdSense (contenido denso y valioso)
    
    NO incluir etiquetas <html>, <head>, <body> ni <h1>.
    Empezar directamente con el contenido del artículo.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"<p>Error al generar contenido: {str(e)}</p>"


def generate_featured_image(title: str) -> str:
    """
    Genera una imagen destacada para el blog usando DALL-E 3.
    
    Args:
        title: El título del artículo
        
    Returns:
        str: URL de la imagen generada
    """
    client = _get_openai_client()
    
    prompt = f"""
    Imagen profesional y cálida para un artículo médico sobre: "{title}".
    
    Estilo: Fotografía editorial suave, colores pastel (rosa, azul claro, beige).
    Tema: Relacionado con maternidad, embarazo o salud femenina.
    Requisitos: NO incluir texto, NO incluir rostros humanos definidos.
    Ambiente: Luminoso, esperanzador, profesional pero acogedor.
    """
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        return f"error:{str(e)}"


def generate_seo_metadata(title: str, content: str) -> dict:
    """
    Genera metadatos SEO para el artículo.
    
    Args:
        title: Título del artículo
        content: Contenido del artículo
        
    Returns:
        dict con meta_description, keywords, slug_sugerido
    """
    model = _get_gemini_model()
    
    # Truncar contenido para el prompt
    content_preview = content[:1000] if len(content) > 1000 else content
    
    prompt = f"""
    Genera metadatos SEO para este artículo:
    Título: {title}
    Contenido (preview): {content_preview}
    
    Devuelve ÚNICAMENTE un JSON válido (sin markdown) con:
    {{
        "meta_description": "descripción de 150-160 caracteres",
        "keywords": ["keyword1", "keyword2", "keyword3"],
        "slug_sugerido": "url-amigable-del-articulo"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except:
        return {
            "meta_description": "",
            "keywords": [],
            "slug_sugerido": ""
        }
