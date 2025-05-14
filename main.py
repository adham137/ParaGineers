import sys
import os
import argparse
from agents.orchestrator import Orchestrator
from utils import Logger, LogColors 
import time 

AGENT_NAME = "MainScript"

if __name__ == "__main__":
    Logger.info("Application started.", AGENT_NAME, LogColors.MAIN)
    
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="Parallelize C code using OpenMP or MPI")
    parser.add_argument("source_file", help="Path to the C source file to parallelize")
    parser.add_argument("-p", "--project-dir", help="Root directory of the C project")
    parser.add_argument("-i", "--include-dirs", nargs='+', help="Include directories (relative to project dir)")
    parser.add_argument("-f", "--extra-files", nargs='+', help="Additional C files to compile")
    parser.add_argument("-c", "--compiler-flags", nargs='+', help="Additional compiler flags")
    
    # Parse arguments
    args = parser.parse_args()
    
    source_file_path = args.source_file
    if not os.path.isfile(source_file_path):
        Logger.error(f"Source file not found: {source_file_path}", AGENT_NAME)
        sys.exit(1)
    
    # Set project directory
    project_dir = args.project_dir if args.project_dir else os.path.dirname(source_file_path)
    
    # Set results directory
    results_dir = os.path.join(os.path.dirname(__file__) or ".", "results")
    if not os.path.exists(results_dir):
        try:
            os.makedirs(results_dir)
            Logger.info(f"Created results directory: {results_dir}", AGENT_NAME, LogColors.MAIN)
        except OSError as e:
            Logger.error(f"Could not create results directory {results_dir}: {e}", AGENT_NAME)
            results_dir = os.path.dirname(source_file_path)
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(source_file_path))[0]
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_filename = f"output_{base_name}_{timestamp}.c"
    output_file_path = os.path.join(results_dir, output_filename)
    
    # Log input parameters
    Logger.info(f"Input C file: {source_file_path}", AGENT_NAME, LogColors.MAIN)
    Logger.info(f"Project directory: {project_dir}", AGENT_NAME, LogColors.MAIN)
    if args.include_dirs:
        Logger.info(f"Include directories: {args.include_dirs}", AGENT_NAME, LogColors.MAIN)
    if args.extra_files:
        Logger.info(f"Extra C files: {args.extra_files}", AGENT_NAME, LogColors.MAIN)
    if args.compiler_flags:
        Logger.info(f"Additional compiler flags: {args.compiler_flags}", AGENT_NAME, LogColors.MAIN)
    Logger.info(f"Output parallelized C file will be: {output_file_path}", AGENT_NAME, LogColors.MAIN)
    
    # Create compilation context with all parameters
    compilation_context = {
        "project_dir": project_dir,
        "include_dirs": args.include_dirs,
        "extra_files": args.extra_files,
        "extra_flags": args.compiler_flags
    }
    
    # Initialize orchestrator and run the parallelization
    orchestrator = Orchestrator()
    try:
        parallel_code = orchestrator.run(source_file_path, compilation_context)
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