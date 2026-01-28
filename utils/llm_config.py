import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(model_name: str = "gemini-2.0-flash", temperature: float = 0.7):
    """
    Factory para obtener el modelo de chat adecuado según el nombre.
    Soporta modelos de OpenAI (gpt-*) y Google Gemini (gemini-*).
    """
    api_key_openai = os.environ.get("OPENAI_API_KEY")
    api_key_gemini = os.environ.get("GEMINI_API_KEY")

    if model_name.startswith("gpt-"):
        if not api_key_openai:
            raise ValueError("OPENAI_API_KEY no está configurada.")
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key_openai
        )
    elif "gemini" in model_name:
        if not api_key_gemini:
             # A veces se llama diferente en entorno, pero asumimos el estándar
             raise ValueError("GEMINI_API_KEY no está configurada.")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key_gemini,
            convert_system_message_to_human=True # A veces necesario para Gemini antiguos, pero seguro mantener
        )
    else:
        # Default o fallback
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=temperature,
            google_api_key=api_key_gemini
        )
