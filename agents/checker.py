
import subprocess
import os
from utils import Logger, LogColors 

AGENT_NAME = "Checker"

class Checker:
    def compile(self, code: str, use_openmp: bool, src_dir: str):
        temp_file_path = os.path.join(src_dir, "temp.c")
        output_exe_path = os.path.join(src_dir, "temp_exe")

        Logger.info(f"Attempting to compile code. OpenMP: {use_openmp}", AGENT_NAME, LogColors.CHECKER)
        Logger.debug(f"Writing code to temporary file: {temp_file_path}", AGENT_NAME, LogColors.CHECKER)
        Logger.debug(f"Code content:\n---\n{code}\n---", AGENT_NAME, LogColors.CHECKER)

        try:
            with open(temp_file_path, "w") as f:
                f.write(code)
        except IOError as e:
            Logger.error(f"Failed to write temporary C file: {e}", AGENT_NAME)
            return False, f"IOError: Failed to write temporary file {temp_file_path}. Details: {e}"

        compiler = "mpicc" if not use_openmp and "MPI_" in code else "gcc"
        cmd = [compiler, temp_file_path, "-o", output_exe_path, "-O2"]

        if use_openmp:
            cmd.append("-fopenmp")
            if compiler == "mpicc":
                Logger.warning("Using mpicc with -fopenmp. If issues occur, ensure mpicc is OpenMP-aware or use an MPI-enabled gcc.", AGENT_NAME)


        Logger.info(f"Compilation command: {' '.join(cmd)}", AGENT_NAME, LogColors.CHECKER)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30) # Added timeout
            if result.returncode == 0:
                Logger.success("Compilation successful.", AGENT_NAME)
                
                try:
                    os.remove(temp_file_path)
                    os.remove(output_exe_path)
                except OSError as e:
                    Logger.warning(f"Could not clean up temporary files: {e}", AGENT_NAME)
                return True, ""
            else:
                Logger.warning(f"Compilation failed. Return code: {result.returncode}", AGENT_NAME)
                Logger.error(f"Compiler errors:\n{result.stderr}", AGENT_NAME)
                return False, result.stderr
        except subprocess.TimeoutExpired:
            Logger.error("Compilation timed out.", AGENT_NAME)
            return False, "Compilation timed out after 30 seconds."
        except FileNotFoundError:
            Logger.error(f"Compiler '{compiler}' not found. Ensure it is installed and in PATH.", AGENT_NAME)
            return False, f"Compiler '{compiler}' not found. Please install it or check your PATH."
        except Exception as e:
            Logger.error(f"An unexpected error occurred during compilation: {e}", AGENT_NAME)
            return False, f"Unexpected compilation error: {e}"