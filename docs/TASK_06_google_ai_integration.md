# Role Definition
You are a Senior AI Engineer specializing in LangChain and Google Gemini integration.
Your task is to implement the **AI Enrichment Layer** using **Google's Generative AI**.

# Project Context
- **Goal:** Generate summaries and embeddings for articles in PostgreSQL.
- **Change Log:** We switched from OpenAI to **Google Gemini**.
- **Critical Requirement:** Google's embedding model uses **768 dimensions**, whereas the previous schema (OpenAI) used 1536. We MUST migrate the database schema.

# Tech Stack
- **Provider:** Google Generative AI (Gemini).
- **LLM:** `gemini-1.5-flash` (Fast & Efficient).
- **Embedding:** `models/text-embedding-004` (768 Dimensions).
- **Library:** `langchain-google-genai`.

# Implementation Plan

## 1. Dependencies (`requirements.txt`)
Update the file to include:
- `langchain-google-genai`
- Remove `langchain-openai` if present.

## 2. Database Schema Migration (`locusum_ingestor/migrations/alter_vector_dim.sql`)
Create a SQL script (or Python function) to fix the vector dimension mismatch.
```sql
-- Ensure the pgvector extension is loaded
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop the old column or alter type (Altering type with data might fail, better to clear and reset for dev)
TRUNCATE TABLE articles; -- Clean slate for development
ALTER TABLE articles ALTER COLUMN embedding TYPE vector(768);

3. AI Service Module (locusum_ingestor/services/ai_service.py)
Create AIService class:

Initialization:

Use ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=...).

Use GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=...).

Method summarize(text):

Prompt: "You are a local news reporter. Summarize the following text into 3 bullet points in Korean."

Method embed(text):

Returns a list of floats (length 768).

4. AI Worker (locusum_ingestor/ai_worker.py)
Create the worker logic:

Fetch articles where summary IS NULL.

Process using AIService.

Update PostgreSQL with the new summary and 768-dim embedding.

Use asyncio for concurrent processing if possible.

5. Environment Variables (.env)
Remind me to set:

GOOGLE_API_KEY=... (Get this from Google AI Studio).

Output Request
Provide the updated requirements.txt.

Provide the code for ai_service.py using langchain-google-genai.

Provide the ai_worker.py script.

Provide the Python code or SQL command to execute the DB schema migration (change vector dimension to 768).