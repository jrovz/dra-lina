"""
Servicios de IA para generación de contenido.
Wrapper que reutiliza la lógica existente en utils/ai_services.py.
"""
import sys
import os

# Añadir el directorio raíz al path para importar utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.ai_services import (
    research_topic,
    generate_blog_draft,
    generate_seo_metadata,
    refine_block_content,
    generate_featured_image,
    analyze_seo
)

__all__ = [
    'research_topic',
    'generate_blog_draft',
    'generate_seo_metadata',
    'refine_block_content',
    'generate_featured_image',
    'analyze_seo'
]
