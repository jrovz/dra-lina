from typing import List
from pydantic import BaseModel, Field

class ResearchResult(BaseModel):
    """Esquema de resultados de investigación."""
    puntos_clave: List[str] = Field(description="Puntos clave encontrados sobre el tema.")
    preguntas_frecuentes: List[str] = Field(description="Preguntas comunes que tienen los pacientes sobre este tema.")
    keywords_seo: List[str] = Field(description="Palabras clave relevantes para SEO relacionadas con la investigación.")

class SeoMetadataSchema(BaseModel):
    """Esquema para metadatos SEO."""
    meta_description: str = Field(description="Descripción optimizada para motores de búsqueda (150-160 caracteres).")
    keywords: List[str] = Field(description="Lista de palabras clave objetivo.")
    slug_sugerido: str = Field(description="URL amigable sugerida para el artículo (ej: beneficios-yoga-embarazo).")

class BlogDraftSchema(BaseModel):
    """Esquema opcional si quisiéramos estructurar el blog completo (aunque suele ser HTML libre)."""
    # Por ahora mantendremos el blog como string HTML, pero esto queda listo para el futuro
    title: str
    content_html: str
