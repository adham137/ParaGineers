import sys, os
from agents.orchestrator import Orchestrator

if __name__ == "__main__":
    source = sys.argv[1]
    output = os.path.join(os.path.dirname(source), "output.c")
    orchestrator = Orchestrator()
    parallel_code = orchestrator.run(source)
    with open(output,"w") as f:
        f.write(parallel_code)
    print(f"Parallelized code saved to {output}")
