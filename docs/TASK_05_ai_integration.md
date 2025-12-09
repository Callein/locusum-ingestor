# Role Definition
You are a Senior AI Engineer specializing in LLM applications and Vector Search.
We have a robust ETL pipeline filling the `articles` table in PostgreSQL.
Your task is to implement the **AI Enrichment Layer** using **LangChain**.

# Project Context
- **Current State:** The `articles` table has clean text (`content`), but `summary` and `embedding` columns are NULL.
- **Goal:**
    1. Select articles where `summary` is NULL.
    2. Generate a **3-line summary** using an LLM.
    3. Generate **Vector Embeddings** (1536 dimensions) for semantic search.
    4. Update the database records.

# Tech Stack
- **Framework:** `LangChain` (Core), `langchain-openai` (or `langchain-community`).
- **Model (LLM):** `ChatOpenAI` (gpt-4o-mini or gpt-3.5-turbo) OR `Ollama` (Llama 3) - *Implement generic interface.*
- **Model (Embedding):** `OpenAIEmbeddings` (text-embedding-3-small).
- **Database:** `SQLModel` + `pgvector`.

# Implementation Requirements

## 1. Dependency Management (`requirements.txt`)
Add:
- `langchain`
- `langchain-openai`
- `python-dotenv`
- `tiktoken`

## 2. AI Service Module (`locusum_ingestor/services/ai_service.py`)
Create a class `AIService` using LangChain's `Chain` or `Runnable`.
- **Method `summarize(text: str) -> str`**:
    - System Prompt: "You are a professional news editor. Summarize the following local news into 3 concise bullet points in Korean."
    - Handle token limits (truncate text if too long).
- **Method `embed(text: str) -> List[float]`**:
    - Use `text-embedding-3-small` to generate vectors.

## 3. AI Worker (`locusum_ingestor/ai_worker.py`)
Create a processing script:
- Fetch batch of articles (e.g., 10 at a time) where `summary IS NULL`.
- Process asynchronously if possible (to handle API latency).
- **Critical:** Update the `articles` table with the generated `summary` and `embedding`.
- Log success/failure.

## 4. Configuration (`.env`)
Remind me to set:
- `OPENAI_API_KEY=sk-...`

# Output Request
1. Provide the updated `requirements.txt`.
2. Provide the complete code for `ai_service.py`.
3. Provide the `ai_worker.py` script.
4. Explain how to switch between OpenAI and Ollama in the code.