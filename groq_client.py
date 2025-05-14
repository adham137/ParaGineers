import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from config import Config
load_dotenv()

llm = ChatGroq(
    model= Config.MODEL_NAME,
    temperature=Config.TEMP,
    max_tokens=Config.MAX_TOKENS,
    max_retries=Config.MAX_RETRIES,
)

def send_prompt(prompt: str) -> str:
    """
    Send a single-turn chat prompt to the Groq model via LangChain.
    Returns the raw text of the model's reply.
    """
    ai_message = llm.invoke(prompt)
    return ai_message.content if hasattr(ai_message, "content") else str(ai_message)
