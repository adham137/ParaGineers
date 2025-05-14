from groq_client import send_prompt
from config import Config

MPI_PROCESS_PROMPT = Config.MPI_PROCESS_PROMPT
MPI_REFINE_PROMPT = Config.MPI_REFINE_PROMPT

class MPIExpert:
    def process(self, mcp_msg):
        code = mcp_msg["payload"]["code"]
        prompt = f"{MPI_PROCESS_PROMPT}{code}"
        new_code = send_prompt(prompt)
        return {
            "agent_id": "mpi_expert",
            "context_id": mcp_msg["context_id"],
            "payload": {"code": new_code},
            "metadata": mcp_msg["metadata"]
        }

    def refine(self, mcp_msg):
        code = mcp_msg["payload"]["code"]
        errors = mcp_msg["payload"].get("errors", "")
        prompt = f"// Compilation errors:\n{errors}\n {MPI_REFINE_PROMPT}{code}"
        new_code = send_prompt(prompt)
        mcp_msg["payload"]["code"] = new_code
        return mcp_msg
