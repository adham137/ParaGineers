from groq_client import send_prompt
from config import Config
from utils import Logger, LogColors # Import Logger

AGENT_NAME = "OMPExpert"

class OMPSExpert: 
    def __init__(self):
        Logger.info("OMPExpert initialized.", AGENT_NAME, LogColors.OMP_EXPERT)
        self.original_code_for_refinement = "" # Store original code for refine context


    def process(self, mcp_msg):
        Logger.info("Processing code for OpenMP parallelization.", AGENT_NAME, LogColors.OMP_EXPERT)
        code = mcp_msg["payload"]["code"]
        self.original_code_for_refinement = code

        prompt = Config.OMP_PROCESS_PROMPT_TEMPLATE.format(code=code)
        Logger.debug(f"Process prompt:\n{prompt}", AGENT_NAME, LogColors.OMP_EXPERT)

        new_code = send_prompt(prompt)
        Logger.info("Received processed code from LLM.", AGENT_NAME, LogColors.OMP_EXPERT)
        Logger.debug(f"New OpenMP code (raw from LLM):\n---\n{new_code}\n---", AGENT_NAME, LogColors.OMP_EXPERT)


        return {
            "agent_id": AGENT_NAME,
            "context_id": mcp_msg["context_id"],
            "payload": {"code": new_code, "original_code": code}, # Include original_code
            "metadata": mcp_msg["metadata"]
        }

    def refine(self, mcp_msg):
        Logger.info("Refining OpenMP code based on errors.", AGENT_NAME, LogColors.OMP_EXPERT)
        attempted_code = mcp_msg["payload"]["code"]
        errors = mcp_msg["payload"].get("errors", "No specific errors provided.")
        original_code = mcp_msg["payload"].get("original_code", self.original_code_for_refinement)

        if not original_code: 
            Logger.warning("Original code not available for refinement context. Refinement might be less effective.", AGENT_NAME)
            original_code = attempted_code 

        prompt = Config.OMP_REFINE_PROMPT_TEMPLATE.format(
            original_code=original_code,
            attempted_code=attempted_code,
            errors=errors
        )
        Logger.debug(f"Refine prompt:\n{prompt}", AGENT_NAME, LogColors.OMP_EXPERT)

        refined_code = send_prompt(prompt)
        Logger.info("Received refined OpenMP code from LLM.", AGENT_NAME, LogColors.OMP_EXPERT)
        Logger.debug(f"Refined OpenMP code (raw from LLM):\n---\n{refined_code}\n---", AGENT_NAME, LogColors.OMP_EXPERT)

        # Update the message payload for the next step (compilation or further refinement)
        mcp_msg["payload"]["code"] = refined_code
        
        return mcp_msg