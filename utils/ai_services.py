"""
Servicios de IA para generación de contenido de blog.
Utiliza Gemini para texto y OpenAI DALL-E 3 para imágenes.

SDK: google-genai v1.60+ (nuevo SDK 2024)
"""
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Clientes de IA (lazy loading)
_openai_client = None
_gemini_client = None
_last_openai_key = None
_last_gemini_key = None

# Modelo de Gemini a usar
GEMINI_MODEL = "gemini-2.0-flash"


def _get_openai_client():
    """Obtiene el cliente de OpenAI (lazy loading con recarga si cambia la key)."""
    global _openai_client, _last_openai_key
    current_key = os.environ.get("OPENAI_API_KEY", "")
    
    if _openai_client is None or current_key != _last_openai_key:
        import openai
        _openai_client = openai.OpenAI(api_key=current_key)
        _last_openai_key = current_key
    return _openai_client


def _get_gemini_client():
    """Obtiene el cliente de Gemini usando el nuevo SDK google-genai."""
    global _gemini_client, _last_gemini_key
    current_key = os.environ.get("GEMINI_API_KEY", "")
    
    if not current_key:
        raise ValueError("GEMINI_API_KEY no está configurada")
    
    if _gemini_client is None or current_key != _last_gemini_key:
        from google import genai
        _gemini_client = genai.Client(api_key=current_key)
        _last_gemini_key = current_key
    return _gemini_client


def _generate_text(prompt: str, model: str = "gemini-2.0-flash") -> str:
    """
    Genera texto usando el modelo seleccionado.
    Soporta tanto Gemini como OpenAI GPT.
    """
    if model.startswith("gpt-"):
        # Usar OpenAI
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    else:
        # Usar Gemini
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text


def research_topic(topic: str, model: str = "gemini-2.0-flash") -> dict:
    """
    Investiga un tema y devuelve puntos clave para el blog.
    
    Args:
        topic: El tema a investigar
        model: El modelo de IA a usar
        
    Returns:
        dict con puntos_clave, preguntas_frecuentes, keywords_seo
    """
    prompt = f"""
    Eres una experta especialista en salud familiar.
    Investiga el tema: "{topic}"
    
    Devuelve ÚNICAMENTE un JSON válido (sin markdown, sin ```json) con esta estructura:
    {{
        "puntos_clave": ["punto 1", "punto 2", "punto 3", "punto 4", "punto 5"],
        "preguntas_frecuentes": ["pregunta 1", "pregunta 2", "pregunta 3"],
        "keywords_seo": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    }}
    """
    
    try:
        text = _generate_text(prompt, model=model)
        text = text.strip()
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


def generate_blog_draft(topic: str, tone: str = "profesional y empático", model: str = "gemini-2.0-flash") -> str:
    """
    Genera un borrador completo de blog usando IA.
    
    Args:
        topic: El tema del artículo
        tone: El tono deseado para el contenido
        model: El modelo de IA a usar
        
    Returns:
        str: Contenido HTML del artículo
    """
    prompt = f"""
    Eres la Dra. Lina, una reconocida especialista en salud familiar.
    Escribe un artículo de blog completo sobre: "{topic}"
    
    Requisitos:
    - Extensión: 800-1200 palabras
    - Tono: Formal y muy respetuoso, pero diseñado para maximizar el engagement. El texto debe ser fácil de leer, entretenido y fluido, captando la atención del lector desde la primera línea.
    - Enfoque: Trata temas de salud general y familiar (no solo ginecología).
    - Formato: HTML con etiquetas <h2>, <h3>, <p>, <ul>, <li>
    - Incluir una introducción muy atractiva (hook).
    - Desarrollar 3-4 secciones principales con subtítulos.
    - Incluir consejos prácticos y aplicables.
    - Terminar con una conclusión memorable y un llamado a la acción.
    - Optimizado para SEO y experiencia de usuario (lectura escaneable).
    
    NO incluir etiquetas <html>, <head>, <body> ni <h1>.
    Empezar directamente con el contenido del artículo.
    """
    
    try:
        return _generate_text(prompt, model=model)
    except Exception as e:
        return f"<p>Error al generar contenido: {str(e)}</p>"


def generate_featured_image(title: str, model: str = "dall-e-3") -> str:
    """
    Genera una imagen destacada para el blog usando el modelo seleccionado.
    
    Args:
        title: El título del artículo
        model: El modelo a usar ("dall-e-3" o "gemini-...")
        
    Returns:
        str: URL de la imagen generada (remota o local)
    """
    prompt = f"""
    Imagen profesional y cálida para un artículo médico sobre: "{title}".
    
    Estilo: Fotografía editorial suave, iluminación natural y colores cálidos.
    Tema: Salud familiar integral, crianza, bienestar, o estilo de vida saludable (incluyendo padres, madres, niños).
    Requisitos: NO incluir texto. NO mostrar rostros definidos (usar desenfoque, de espaldas, o detalles).
    Ambiente: Luminoso, acogedor, transmitiendo calma y unión familiar.
    """
    
    try:
        if model.lower().startswith("gemini"):
            # Generación con Gemini (Imagen 3)
            client = _get_gemini_client()
            
            # Nota: El modelo de imagen de Gemini suele ser 'gemini-2.0-flash' o específico como 'imagen-3.0-generate-001'
            # Asumimos que el modelo pasado es capaz de generar imágenes o usamos el default
            model_to_use = model if "flash" in model else "gemini-2.0-flash"

            response = client.models.generate_content(
                model=model_to_use,
                contents=prompt,
                config={'response_mime_type': 'image/png'} 
            )
            
            # Buscar la parte de imagen en la respuesta
            image_data = None
            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        image_data = part.inline_data.data
                        break
            
            # Si no hay inline_data, intentamos ver si el texto devolvió error o algo inesperado
            if not image_data:
                 return "error: No se recibió imagen de Gemini."

            # Guardar imagen localmente
            import base64
            import uuid
            from datetime import datetime
            
            # Gemini devuelve bytes crudos o base64 dependiendo del SDK, google-genai suele manejarlo internamente
            # En response.parts[0].inline_data.data vienen los bytes
            
            filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
            save_path = os.path.join("static", "generated_images", filename)
            
            # Asegurar directorio
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, "wb") as f:
                f.write(image_data)
                
            return f"/static/generated_images/{filename}"

        else:
            # Generación con OpenAI DALL-E 3
            client = _get_openai_client()
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                style="natural",
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
        text = _generate_text(prompt)
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return json.loads(text)
    except:
        return {
            "meta_description": "",
            "keywords": [],
            "slug_sugerido": ""
        }


def refine_block_content(content: str, action: str, context: str = "", model: str = "gemini-2.0-flash") -> str:
    """
    Refina el contenido de un bloque específico usando IA.
    
    Args:
        content: El texto del bloque a refinar
        action: La acción a realizar (expand, shorten, formal, casual, scientific)
        context: Contexto adicional (título del artículo, etc.)
        model: El modelo de IA a usar
        
    Returns:
        str: El contenido refinado
    """
    action_prompts = {
        "expand": """
            Expande este párrafo con más detalles, ejemplos y explicaciones.
            Mantén el mismo tono y estilo. Genera 2-3 párrafos adicionales.
            Devuelve SOLO el texto expandido, sin etiquetas HTML.
        """,
        "shorten": """
            Resume este texto de forma concisa, manteniendo las ideas principales.
            Reduce a 1-2 oraciones claras y directas.
            Devuelve SOLO el texto resumido.
        """,
        "formal": """
            Reescribe este texto con un tono más formal y profesional.
            Usa vocabulario técnico apropiado para contenido médico.
            Devuelve SOLO el texto reescrito.
        """,
        "casual": """
            Reescribe este texto con un tono más cercano y empático.
            Hazlo fácil de entender para pacientes no especializadas.
            Devuelve SOLO el texto reescrito.
        """,
        "scientific": """
            Reescribe con enfoque científico, añadiendo datos o estadísticas relevantes.
            Mantén la precisión médica.
            Devuelve SOLO el texto reescrito.
        """
    }
    
    base_prompt = action_prompts.get(action, action_prompts["expand"])
    
    full_prompt = f"""
    Eres la Dra. Lina, especialista en salud familiar.
    {f'Contexto del artículo: {context}' if context else ''}
    
    Texto original:
    "{content}"
    
    {base_prompt}
    """
    
    try:
        return _generate_text(full_prompt, model=model).strip()
    except Exception as e:
        return f"Error: {str(e)}"



def analyze_seo(title: str, content: str, keywords: list) -> dict:
    """
    Analiza el SEO del contenido actual.
    
    Args:
        title: Título del artículo
        content: Contenido HTML del artículo
        keywords: Lista de keywords objetivo
        
    Returns:
        dict con score, issues, y sugerencias
    """
    # Limpiar HTML para análisis
    clean_content = re.sub(r'<[^>]+>', ' ', content)
    clean_content = clean_content.lower()
    word_count = len(clean_content.split())
    
    issues = []
    score = 100
    
    # Verificar longitud
    if word_count < 300:
        issues.append("⚠️ Contenido muy corto (< 300 palabras)")
        score -= 20
    elif word_count < 600:
        issues.append("💡 Considera expandir a 600+ palabras")
        score -= 10
    
    # Verificar título
    if len(title) < 30:
        issues.append("⚠️ Título muy corto")
        score -= 10
    elif len(title) > 60:
        issues.append("⚠️ Título muy largo para SEO")
        score -= 5
    
    # Verificar keywords
    keyword_presence = {}
    for kw in keywords[:5]:  # Analizar top 5 keywords
        kw_lower = kw.lower()
        count = clean_content.count(kw_lower)
        keyword_presence[kw] = count
        if count == 0:
            issues.append(f"❌ Keyword '{kw}' no encontrada")
            score -= 10
        elif count < 2:
            issues.append(f"💡 Usa más '{kw}' (actualmente: {count})")
            score -= 5
    
    # Verificar estructura HTML
    has_h2 = '<h2' in content.lower()
    has_h3 = '<h3' in content.lower()
    has_list = '<ul' in content.lower() or '<ol' in content.lower()
    
    if not has_h2:
        issues.append("❌ Falta encabezado H2")
        score -= 15
    if not has_h3:
        issues.append("💡 Añadir subtítulos H3")
        score -= 5
    if not has_list:
        issues.append("💡 Añadir listas para mejor lectura")
        score -= 5
    
    score = max(0, min(100, score))
    
    return {
        "score": score,
        "word_count": word_count,
        "issues": issues,
        "keyword_presence": keyword_presence,
        "structure": {
            "has_h2": has_h2,
            "has_h3": has_h3,
            "has_list": has_list
        }
    }
