from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from .llm_config import get_llm
from .schemas import ResearchResult

# Agente de Investigación Profunda (Deep Research)
# Por ahora simularemos la búsqueda ya que no tenemos una API Key de búsqueda configurada (como Tavily)
# En el futuro, reemplazaremos el nodo "search_web" con una llamada real.

class ResearchState(TypedDict):
    topic: str
    steps: List[str]
    content: List[str]
    final_report: dict

def plan_node(state: ResearchState):
    """Genera un plan de investigación (preguntas clave)."""
    print(f"--- Planeando investigación sobre: {state['topic']} ---")
    llm = get_llm("gemini-2.0-flash")
    prompt = f"Para investigar exhaustivamente sobre '{state['topic']}', lista 3 preguntas de búsqueda específicas y breves."
    response = llm.invoke(prompt)
    # Simple splitting por líneas para simular pasos
    steps = [line.strip('- *') for line in response.content.split('\n') if line.strip()][:3]
    return {"steps": steps}

def search_node(state: ResearchState):
    """(Simulado) Busca información para cada paso."""
    print("--- Buscando información ---")
    steps = state['steps']
    # En producción: Aquí iteraríamos steps y llamaríamos a Tavily/Google
    # Simulación: Usamos el LLM para 'alucinar' información precisa basada en su conocimiento interno
    # OJO: Esto es temporal hasta tener API de Search.
    
    llm = get_llm("gemini-2.0-flash")
    gathered_content = []
    
    for step in steps:
        fake_search_prompt = f"Imagina que buscaste '{step}' en Google. Resume la información más relevante y actual que encontrarías (3-4 frases)."
        res = llm.invoke(fake_search_prompt)
        gathered_content.append(f"Resultados para '{step}':\n{res.content}")
        
    return {"content": gathered_content}

def synthesize_node(state: ResearchState):
    """Sintetiza la información en el formato final."""
    print("--- Sintetizando reporte ---")
    llm = get_llm("gemini-2.0-flash")
    structured_llm = llm.with_structured_output(ResearchResult)
    
    all_content = "\n\n".join(state['content'])
    prompt = f"""
    Tema: {state['topic']}
    
    Información recopilada:
    {all_content}
    
    Basado en esto, genera el reporte de investigación estructurado.
    """
    
    result = structured_llm.invoke(prompt)
    return {"final_report": result.dict()} # Devolvemos dict para serialización fácil

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
