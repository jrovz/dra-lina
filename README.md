# Dra. Lina Web Platform

Plataforma web para la Dra. Lina, desarrollada con **Flask**. Esta aplicación gestiona citas médicas y cuenta con un **Estudio de Contenido impulsado por IA** para la generación automatizada de artículos de blog educativos sobre salud familiar.

## 🚀 Características Principales

*   **Gestión de Citas**: Sistema de reservas para pacientes (lógica en `utils/booking_logic.py`).
*   **Gestión de Contenidos (Blog)**: Editor de blog con soporte de IA.
*   **Agente de Investigación IA**: Utiliza **LangChain** y **LangGraph** para investigar temas médicos, generar estructuras y redactar borradores completos.
*   **Generación de Imágenes**: Integración con DALL-E 3 y Google Imagen 3.
*   **Admin Panel**: Panel administrativo seguro para gestionar el sitio.

## 🛠️ Stack Tecnológico

*   **Backend**: Python, Flask, SQLAlchemy.
*   **Base de Datos**: PostgreSQL.
*   **IA & Agentes**:
    *   **LangChain**: Orquestación de LLMs y Structured Output.
    *   **LangGraph**: Flujos de trabajo agénticos (Investigación Profunda).
    *   **Modelos**: GPT-4o / DALL-E 3 (OpenAI) y Gemini 2.0 Flash (Google).

## ⚙️ Configuración e Instalación

### 1. Requisitos Previos
*   Python 3.10+
*   PostgreSQL

### 2. Instalación

Clona el repositorio y crea un entorno virtual:

```bash
git clone <url-del-repo>
cd dra-lina-web
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate # Mac/Linux
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

### 3. Configuración (.env)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://usuario:password@localhost:5432/dra_lina_db

# Configuración de Correo (Flask-Mail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password

# --- API Keys para Inteligencia Artificial ---
# Requerido para generación de texto/imágenes con OpenAI
OPENAI_API_KEY=sk-proj-...

# Requerido para Gemini y LangGraph Agents
GEMINI_API_KEY=AIzaSy...
```

### 4. Ejecución

Inicializa la base de datos (si es la primera vez):

```bash
flask db upgrade
# Opcional: Poblar datos de prueba
python seed_data.py
```

Ejecuta el servidor de desarrollo:

```bash
flask run --debug
```

Accede a `http://localhost:5000`.

## 🤖 Módulos de IA (`utils/`)

El núcleo de inteligencia artificial ha sido refactorizado para usar patrones robustos:

*   **`ai_services.py`**: Fachada principal. Expone funciones como `generate_blog_draft` y `research_topic`.
*   **`research_graph.py`**: Implementación de un agente en **LangGraph** que planifica, busca (simulado por ahora) y sintetiza información.
*   **`llm_config.py`**: Configuración centralizada de modelos.
*   **`schemas.py`**: Modelos Pydantic para validar estrictamente las salidas de la IA (JSON outputs).

## 🤝 Contribuir

1.  Usa siempre el entorno virtual.
2.  Si añades nuevas dependencias, actualiza `requirements.txt`.
3.  Para nuevas funcionalidades de IA, sigue la guía en `.agent/skills/langchain-langgraph-expert`.
