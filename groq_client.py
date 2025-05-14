import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from config import Config
from utils import Logger, LogColors 

load_dotenv(override=True)

AGENT_NAME = "GroqClient"

try:
    llm = ChatGroq(
        model=Config.MODEL_NAME,
        temperature=Config.TEMP,
        max_tokens=Config.MAX_TOKENS,
        max_retries=Config.MAX_RETRIES,
    )
    Logger.success(f"Successfully initialized Groq LLM with model: {Config.MODEL_NAME}", AGENT_NAME)
except Exception as e:
    Logger.error(f"Failed to initialize Groq LLM: {e}", AGENT_NAME)
    llm = None

def send_prompt(prompt: str) -> str:
    """
    Send a single-turn chat prompt to the Groq model via LangChain.
    Returns the raw text of the model's reply.
    """
    if not llm:
        Logger.error("LLM not initialized. Cannot send prompt.", AGENT_NAME)
        return "// LLM Error: Not initialized"

    Logger.info(f"Sending prompt to LLM (approx {len(prompt)} chars)...", AGENT_NAME, LogColors.GROQ_CLIENT)
    Logger.debug(f"Prompt content:\n---\n{prompt}\n---", AGENT_NAME, LogColors.GROQ_CLIENT)

    try:
        ai_message = llm.invoke(prompt)
        response_content = ai_message.content if hasattr(ai_message, "content") else str(ai_message)
        Logger.info(f"Received response from LLM (approx {len(response_content)} chars).", AGENT_NAME, LogColors.GROQ_CLIENT)
        Logger.debug(f"Response content:\n---\n{response_content}\n---", AGENT_NAME, LogColors.GROQ_CLIENT)
        
        # Basic cleaning: remove backticks and 'c' if LLM wraps code in ```c ... ```
        if response_content.strip().startswith("```c"):
            response_content = response_content.split("```c", 1)[1]
            if response_content.strip().endswith("```"):
                 response_content = response_content.rsplit("```", 1)[0]
        elif response_content.strip().startswith("```"):
            response_content = response_content.split("```", 1)[1]
            if response_content.strip().endswith("```"):
                response_content = response_content.rsplit("```", 1)[0]

        return response_content.strip()
    except Exception as e:
        Logger.error(f"Error during LLM invocation: {e}", AGENT_NAME)
        return f"// LLM Invocation Error: {e}"