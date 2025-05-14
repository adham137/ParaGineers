from groq_client import send_prompt
from config import Config

OMP_PROCESS_PROMPT = Config.OMP_PROCESS_PROMPT
OMP_REFINE_PROMPT = Config.OMP_REFINE_PROMPT

class OMPSExpert:
    def process(self, mcp_msg):
        code = mcp_msg["payload"]["code"]
        prompt = f"{OMP_PROCESS_PROMPT}{code}"
        new_code = send_prompt(prompt)
        return {
            "agent_id": "omp_expert",
            "context_id": mcp_msg["context_id"],
            "payload": {"code": new_code},
            "metadata": mcp_msg["metadata"]
        }

    def refine(self, mcp_msg):
        code = mcp_msg["payload"]["code"]
        errors = mcp_msg["payload"].get("errors", "")
        prompt = f"// Compilation errors:\n{errors}\n {OMP_REFINE_PROMPT} {code}"
        new_code = send_prompt(prompt)
        # Overwrite payload for next compile
        mcp_msg["payload"]["code"] = new_code
        return mcp_msg
