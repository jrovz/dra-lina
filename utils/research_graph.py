import os
import requests
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from .llm_config import get_llm
from .schemas import ResearchResult, Reference

# Agente de Investigación Profunda (Deep Research)
# Usa SERP API para búsquedas reales y LLM para síntesis.

DEFAULT_MODEL = "gpt-4o"


class ResearchState(TypedDict):
    topic: str
    steps: List[str]
    content: List[str]
    references: List[dict]
    final_report: dict


def _get_model_from_config(config: RunnableConfig) -> str:
    """Extrae el modelo de la configuración o usa el default."""
    return config.get("configurable", {}).get("model", DEFAULT_MODEL)


def plan_node(state: ResearchState, config: RunnableConfig):
    """Genera un plan de investigación (preguntas clave)."""
    model = _get_model_from_config(config)
    print(f"--- Planeando investigación sobre: {state['topic']} (modelo: {model}) ---")
    llm = get_llm(model)
    prompt = f"Para investigar exhaustivamente sobre '{state['topic']}', lista 3 preguntas de búsqueda específicas y breves."
    response = llm.invoke(prompt)
    steps = [line.strip('- *') for line in response.content.split('\n') if line.strip()][:3]
    return {"steps": steps}


def search_node(state: ResearchState, config: RunnableConfig):
    """Busca información usando SERP API (con fallback a simulación)."""
    model = _get_model_from_config(config)
    print(f"--- Buscando información con SERP API ---")
    
    api_key = os.environ.get("SERP_API_KEY")
    steps = state['steps']
    
    gathered_content = []
    references = []
    
    for query in steps:
        if api_key:
            try:
                # Usar SERP API real
                response = requests.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": api_key,
                        "num": 5,
                        "hl": "es"
                    },
                    timeout=10
                )
                data = response.json()
                results = data.get("organic_results", [])
                
                query_content = f"Resultados para '{query}':\n"
                for r in results[:3]:
                    title = r.get("title", "Sin título")
                    link = r.get("link", "")
                    snippet = r.get("snippet", "")
                    
                    references.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
                    query_content += f"- {title}: {snippet}\n"
                
                gathered_content.append(query_content)
                print(f"  ✓ Encontrados {len(results[:3])} resultados para: {query[:50]}...")
                
            except Exception as e:
                print(f"  ⚠ Error SERP API: {e}. Usando fallback...")
                # Fallback a simulación con LLM
                llm = get_llm(model)
                fake_prompt = f"Imagina que buscaste '{query}' en Google. Resume la información más relevante (3-4 frases)."
                res = llm.invoke(fake_prompt)
                gathered_content.append(f"Resultados para '{query}':\n{res.content}")
        else:
            # Sin API key: simulación con LLM
            print(f"  ⚠ SERP_API_KEY no configurada. Usando simulación...")
            llm = get_llm(model)
            fake_prompt = f"Imagina que buscaste '{query}' en Google. Resume la información más relevante (3-4 frases)."
            res = llm.invoke(fake_prompt)
            gathered_content.append(f"Resultados para '{query}':\n{res.content}")
    
    return {"content": gathered_content, "references": references}


def synthesize_node(state: ResearchState, config: RunnableConfig):
    """Sintetiza la información en el formato final, incluyendo referencias."""
    model = _get_model_from_config(config)
    print(f"--- Sintetizando reporte (modelo: {model}) ---")
    llm = get_llm(model)
    structured_llm = llm.with_structured_output(ResearchResult)
    
    all_content = "\n\n".join(state['content'])
    references = state.get('references', [])
    
    # Incluir referencias en el prompt para que el LLM las considere
    refs_text = ""
    if references:
        refs_text = "\n\nFuentes consultadas:\n" + "\n".join(
            f"- {r['title']} ({r['url']})" for r in references[:10]
        )
    
    prompt = f"""
    Tema: {state['topic']}
    
    Información recopilada:
    {all_content}
    {refs_text}
    
    Basado en esto, genera el reporte de investigación estructurado.
    Incluye las referencias relevantes que se usaron.
    """
    
    result = structured_llm.invoke(prompt)
    
    # Asegurar que las referencias del search se incluyan en el resultado
    result_dict = result.model_dump()
    if references and not result_dict.get('references'):
        result_dict['references'] = references[:10]
    
    return {"final_report": result_dict}


# Construcción del Grafo
workflow = StateGraph(ResearchState)

workflow.add_node("planner", plan_node)
workflow.add_node("searcher", search_node)
workflow.add_node("synthesizer", synthesize_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "searcher")
workflow.add_edge("searcher", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compilación
research_app = workflow.compile()
