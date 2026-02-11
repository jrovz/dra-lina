from typing import List, Optional
from pydantic import BaseModel, Field


class Reference(BaseModel):
    """Representa una fuente/referencia de búsqueda web."""
    title: str = Field(description="Título de la fuente")
    url: str = Field(default="", description="URL de la fuente")
    snippet: str = Field(default="", description="Extracto/resumen de la fuente")


class ResearchResult(BaseModel):
    """Esquema de resultados de investigación."""
    puntos_clave: List[str] = Field(description="Puntos clave encontrados sobre el tema.")
    preguntas_frecuentes: List[str] = Field(description="Preguntas comunes que tienen los pacientes sobre este tema.")
    keywords_seo: List[str] = Field(description="Palabras clave relevantes para SEO relacionadas con la investigación.")
    references: Optional[List[Reference]] = Field(default_factory=list, description="Referencias/fuentes usadas en la investigación.")

class SeoMetadataSchema(BaseModel):
    """Esquema para metadatos SEO."""
    meta_description: str = Field(description="Descripción optimizada para motores de búsqueda (150-160 caracteres).")
    keywords: List[str] = Field(description="Lista de palabras clave objetivo.")
    slug_sugerido: str = Field(description="URL amigable sugerida para el artículo (ej: beneficios-yoga-embarazo).")

class ContentBlock(BaseModel):
    """Representa un bloque de contenido estructurado."""
    type: str = Field(description="Tipo de bloque: 'heading', 'subheading', 'paragraph', 'list', 'quote'")
    content: str = Field(description="Contenido del bloque. Para listas, usar saltos de línea para separar items.")

class BlogDraftSchema(BaseModel):
    """Esquema estructurado para borradores de blog."""
    title: str = Field(description="Título principal del artículo (H1).")
    blocks: List[ContentBlock] = Field(description="Lista ordenada de bloques de contenido del artículo.")
