from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from .llm_config import get_llm
from .schemas import ResearchResult

# Agente de Investigación Profunda (Deep Research)
# Usa un modelo configurable via RunnableConfig en lugar de hardcoding.

DEFAULT_MODEL = "gemini-2.0-flash"

class ResearchState(TypedDict):
    topic: str
    steps: List[str]
    content: List[str]
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
    """Busca información para cada paso. (Simulado - requiere API de búsqueda real)."""
    model = _get_model_from_config(config)
    print(f"--- Buscando información (modelo: {model}) ---")
    steps = state['steps']
    # TODO: Integrar TavilySearchResults o DuckDuckGoSearchResults aquí.
    # Simulación actual usa LLM.
    
    llm = get_llm(model)
    gathered_content = []
    
    for step in steps:
        fake_search_prompt = f"Imagina que buscaste '{step}' en Google. Resume la información más relevante y actual que encontrarías (3-4 frases)."
        res = llm.invoke(fake_search_prompt)
        gathered_content.append(f"Resultados para '{step}':\n{res.content}")
        
    return {"content": gathered_content}

def synthesize_node(state: ResearchState, config: RunnableConfig):
    """Sintetiza la información en el formato final."""
    model = _get_model_from_config(config)
    print(f"--- Sintetizando reporte (modelo: {model}) ---")
    llm = get_llm(model)
    structured_llm = llm.with_structured_output(ResearchResult)
    
    all_content = "\n\n".join(state['content'])
    prompt = f"""
    Tema: {state['topic']}
    
    Información recopilada:
    {all_content}
    
    Basado en esto, genera el reporte de investigación estructurado.
    """
    
    result = structured_llm.invoke(prompt)
    return {"final_report": result.dict()}

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
