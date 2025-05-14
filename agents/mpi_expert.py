from groq_client import send_prompt
from config import Config
from utils import Logger, LogColors # Import Logger

AGENT_NAME = "MPIExpert"

class MPIExpert:
    def __init__(self):
        Logger.info("MPIExpert initialized.", AGENT_NAME, LogColors.MPI_EXPERT)
        self.original_code_for_refinement = "" 

    def process(self, mcp_msg):
        Logger.info("Processing code for MPI parallelization.", AGENT_NAME, LogColors.MPI_EXPERT)
        code = mcp_msg["payload"]["code"]
        self.original_code_for_refinement = code

        prompt = Config.MPI_PROCESS_PROMPT_TEMPLATE.format(code=code)
        Logger.debug(f"Process prompt:\n{prompt}", AGENT_NAME, LogColors.MPI_EXPERT)

        new_code = send_prompt(prompt)
        Logger.info("Received processed MPI code from LLM.", AGENT_NAME, LogColors.MPI_EXPERT)
        Logger.debug(f"New MPI code (raw from LLM):\n---\n{new_code}\n---", AGENT_NAME, LogColors.MPI_EXPERT)

        return {
            "agent_id": AGENT_NAME,
            "context_id": mcp_msg["context_id"],
            "payload": {"code": new_code, "original_code": code}, 
            "metadata": mcp_msg["metadata"]
        }

    def refine(self, mcp_msg):
        Logger.info("Refining MPI code based on errors.", AGENT_NAME, LogColors.MPI_EXPERT)
        attempted_code = mcp_msg["payload"]["code"]
        errors = mcp_msg["payload"].get("errors", "No specific errors provided.")
        original_code = mcp_msg["payload"].get("original_code", self.original_code_for_refinement)

        if not original_code:
            Logger.warning("Original code not available for MPI refinement context.", AGENT_NAME)
            original_code = attempted_code

        prompt = Config.MPI_REFINE_PROMPT_TEMPLATE.format(
            original_code=original_code,
            attempted_code=attempted_code,
            errors=errors
        )
        Logger.debug(f"Refine prompt:\n{prompt}", AGENT_NAME, LogColors.MPI_EXPERT)

        refined_code = send_prompt(prompt)
        Logger.info("Received refined MPI code from LLM.", AGENT_NAME, LogColors.MPI_EXPERT)
        Logger.debug(f"Refined MPI code (raw from LLM):\n---\n{refined_code}\n---", AGENT_NAME, LogColors.MPI_EXPERT)
        
        mcp_msg["payload"]["code"] = refined_code
        return mcp_msg