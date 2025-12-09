
import os
import time
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from loguru import logger
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from google.api_core.exceptions import ResourceExhausted

load_dotenv()

class AIService:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

        # Rate Limiting Configuration (Free Tier: 15 RPM)
        self.rpm_limit = 15
        self.min_interval = 60.0 / self.rpm_limit  # 4 seconds
        self.last_call_time = 0.0

        # Gemini 2.5 Flash (Corrected from Lite)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=google_api_key,
            temperature=0.3
        )
        
        # Google Text Embeddings 004 (768 Dimensions)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=google_api_key
        )
        
        # Summarization Prompt (English, Strict Bullet Points)
        self.summary_prompt = PromptTemplate.from_template(
            """
            System: You are a professional news editor.
            Task: Summarize the following news article into 3 concise bullet points in English.
            Constraints:
            - Output ONLY the 3 bullet points.
            - Do NOT include any introductory text like "Here is the summary".
            - Start each bullet point with "* ".
            - Keep it concise and factual.

            Article:
            {text}
            
            Summary (English Bullet Points):
            """
        )
        
        self.summary_chain = self.summary_prompt | self.llm

    def _wait_for_rate_limit(self):
        """Enforce strict 15 RPM limit by waiting."""
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.info(f"Rate Limiting: Sleeping for {sleep_time:.2f}s...")
            time.sleep(sleep_time)
        self.last_call_time = time.time()

    @retry(
        retry=retry_if_exception_type(ResourceExhausted),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        before_sleep=lambda retry_state: logger.warning(f"Rate Limit Hit (429) on [gemini-2.5-flash]. Retrying in {retry_state.next_action.sleep}s...")
    )
    def summarize(self, text: str) -> str:
        """
        Generate a 3-line summary of the text using Gemini.
        Includes automatic retry for 429 errors and rate limiting.
        """
        self._wait_for_rate_limit()
        try:
            # Simple truncation to avoid huge token costs
            truncated_text = text[:10000]
            
            response = self.summary_chain.invoke({"text": truncated_text})
            return response.content.strip()
        except ResourceExhausted as e:
            # Re-raise for tenacity to handle
            raise e
        except RetryError as e:
            # Propagate retry failure up to worker to trigger rollback
            raise e
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return ""

    @retry(
        retry=retry_if_exception_type(ResourceExhausted),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        before_sleep=lambda retry_state: logger.warning(f"Rate Limit Hit (429) on [text-embedding-004]. Retrying in {retry_state.next_action.sleep}s...")
    )
    def embed(self, text: str) -> List[float]:
        """
        Generate vector embedding (768 dims) using Google Embeddings.
        Includes automatic retry for 429 errors and rate limiting.
        """
        self._wait_for_rate_limit()
        try:
            clean_text = text.replace("\n", " ")
            
            vector = self.embeddings.embed_query(clean_text)
            return vector
        except ResourceExhausted as e:
            raise e
        except RetryError as e:
            raise e
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
