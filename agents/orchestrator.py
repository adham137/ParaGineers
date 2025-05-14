import json
import time, os
from agents.omp_expert import OMPSExpert
from agents.mpi_expert import MPIExpert
from agents.checker import Checker
from config import Config

MAX_RETRIES = Config.MAX_RETRIES

class Orchestrator:
    def __init__(self):
        self.omp = OMPSExpert()
        self.mpi = MPIExpert()
        self.checker = Checker()

    def choose_expert(self, code: str):
        return self.mpi if "MPI_" in code else self.omp

    def run(self, source_path: str):
        code = open(source_path).read()
        context_id = f"run-{int(time.time())}"
        expert = self.choose_expert(code)
        mcp_msg = {
            "agent_id": "orchestrator",
            "context_id": context_id,
            "payload": {"code": code},
            "metadata": {"use_openmp": expert==self.omp, "retry": 0}
        }

        for attempt in range(MAX_RETRIES):
            # 1. Ask expert to process
            proc_msg = expert.process(mcp_msg)
            # 2. Compile
            success, errors = self.checker.compile(
                proc_msg["payload"]["code"],
                use_openmp=proc_msg["metadata"]["use_openmp"],
                src_dir=os.path.dirname(source_path)
            )
            if success:
                print("✅ Compilation succeeded")
                return proc_msg["payload"]["code"]
            # 3. On failure, build a refine message
            mcp_msg = {
                "agent_id": "orchestrator",
                "context_id": context_id,
                "payload": {"code": proc_msg["payload"]["code"], "errors": errors},
                "metadata": {"use_openmp": proc_msg["metadata"]["use_openmp"], "retry": attempt+1}
            }
            expert.refine(mcp_msg)
        raise RuntimeError("Failed after retries")
