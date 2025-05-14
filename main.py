import sys
import os
from agents.orchestrator import Orchestrator
from utils import Logger, LogColors 
import time # For timestamp in output filename

AGENT_NAME = "MainScript"

if __name__ == "__main__":
    Logger.info("Application started.", AGENT_NAME, LogColors.MAIN)
    if len(sys.argv) < 2:
        Logger.error("No source file provided. Usage: python main.py <path_to_c_file>", AGENT_NAME)
        sys.exit(1)

    source_file_path = sys.argv[1]
    if not os.path.isfile(source_file_path):
        Logger.error(f"Source file not found: {source_file_path}", AGENT_NAME)
        sys.exit(1)

    
    results_dir = os.path.join(os.path.dirname(__file__) or ".", "results") # Handle running from any dir
    if not os.path.exists(results_dir):
        try:
            os.makedirs(results_dir)
            Logger.info(f"Created results directory: {results_dir}", AGENT_NAME, LogColors.MAIN)
        except OSError as e:
            Logger.error(f"Could not create results directory {results_dir}: {e}", AGENT_NAME)
            
            results_dir = os.path.dirname(source_file_path)


    
    base_name = os.path.splitext(os.path.basename(source_file_path))[0]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_filename = f"output_{base_name}_{timestamp}.c"
    output_file_path = os.path.join(results_dir, output_filename)


    Logger.info(f"Input C file: {source_file_path}", AGENT_NAME, LogColors.MAIN)
    Logger.info(f"Output parallelized C file will be: {output_file_path}", AGENT_NAME, LogColors.MAIN)

    orchestrator = Orchestrator()
    try:
        parallel_code = orchestrator.run(source_file_path)
        Logger.success("Orchestrator run completed successfully.", AGENT_NAME)
        try:
            with open(output_file_path, "w") as f:
                f.write(parallel_code)
            Logger.success(f"Parallelized code saved to {output_file_path}", AGENT_NAME)
        except IOError as e:
            Logger.error(f"Failed to write output file {output_file_path}: {e}", AGENT_NAME)
            print("\n--- BEGIN PARALLELIZED CODE ---\n")
            print(parallel_code)
            print("\n--- END PARALLELIZED CODE ---\n")


    except FileNotFoundError:
        # Error already logged by Orchestrator or initial check
        Logger.error("Terminating due to file not found.", AGENT_NAME)
    except RuntimeError as e:
        Logger.error(f"Parallelization process failed: {e}", AGENT_NAME)
    except Exception as e:
        Logger.error(f"An unexpected error occurred in main: {e}", AGENT_NAME)
    finally:
        Logger.info("Application finished.", AGENT_NAME, LogColors.MAIN)