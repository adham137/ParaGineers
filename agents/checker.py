import subprocess
import os
from utils import Logger, LogColors # Assuming Logger and LogColors are in utils.py

AGENT_NAME = "Checker"

class Checker:
    def compile(self, code: str, use_openmp: bool, src_dir: str):
        """
        Compiles the given C code.
        Args:
            code (str): The C code to compile.
            use_openmp (bool): Whether to include OpenMP flags.
            src_dir (str): The directory of the C project. Compilation will run in this directory.
        Returns:
            tuple: (bool, str) where bool is True on success, False on failure,
                   and str contains error messages if compilation failed.
        """
        
        # Ensure src_dir is an absolute path for clarity, though relative might work.
        absolute_src_dir = os.path.abspath(src_dir)
        Logger.info(f"Compilation will run in directory: {absolute_src_dir}", AGENT_NAME, LogColors.CHECKER)

        temp_c_filename = "temp_generated_code.c" # Name for the temporary C file
        temp_exe_filename = "temp_compiled_exe"   # Name for the temporary executable
        
        # Path for Python to write the C code
        temp_c_filepath_py = os.path.join(absolute_src_dir, temp_c_filename)
        # Path for Python to potentially remove the executable
        temp_exe_filepath_py = os.path.join(absolute_src_dir, temp_exe_filename)


        Logger.info(f"Attempting to compile code. OpenMP: {use_openmp}", AGENT_NAME, LogColors.CHECKER)
        Logger.debug(f"Writing code to temporary file: {temp_c_filepath_py}", AGENT_NAME, LogColors.CHECKER)
        # Logger.debug(f"Code content:\n---\n{code}\n---", AGENT_NAME, LogColors.CHECKER) # Can be very verbose

        try:
            with open(temp_c_filepath_py, "w") as f:
                f.write(code)
        except IOError as e:
            Logger.error(f"Failed to write temporary C file '{temp_c_filepath_py}': {e}", AGENT_NAME)
            return False, f"IOError: Failed to write temporary file {temp_c_filepath_py}. Details: {e}"

        # Determine the compiler
        # For Cygwin, 'gcc' should be in the PATH within the Cygwin environment.
        # If MPI is used, 'mpicc' is preferred. It's assumed mpicc is also in PATH and Cygwin-compatible if needed.
        compiler = "mpicc" if not use_openmp and "MPI_" in code.upper() else "gcc"
        Logger.info(f"Using compiler: {compiler}", AGENT_NAME, LogColors.CHECKER)
        
        # Command construction: file paths are relative to `cwd` (src_dir)
        cmd = [compiler, temp_c_filename, "-o", temp_exe_filename, "-O3"]
        if use_openmp:
            cmd.append("-fopenmp")
            if compiler == "mpicc":
                Logger.warning("Using mpicc with -fopenmp. Ensure your Cygwin mpicc supports this or is a wrapper around an OpenMP-enabled gcc.", AGENT_NAME)
        
        Logger.info(f"Compilation command: {' '.join(cmd)}", AGENT_NAME, LogColors.CHECKER)
        Logger.info(f"Executing command in directory: {absolute_src_dir}", AGENT_NAME, LogColors.CHECKER)

        try:
            # Execute the compilation command with cwd set to the source directory
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=absolute_src_dir,
                timeout=60 # Increased timeout slightly
            )

            if result.returncode == 0:
                Logger.success(f"Compilation successful in {absolute_src_dir}.", AGENT_NAME)
                # Clean up temporary files on success
                try:
                    os.remove(temp_c_filepath_py)
                    # temp_exe_filepath_py might have .exe on Windows even under Cygwin if gcc adds it
                    if os.path.exists(temp_exe_filepath_py):
                        os.remove(temp_exe_filepath_py)
                    elif os.path.exists(temp_exe_filepath_py + ".exe"): # Check for .exe extension
                         os.remove(temp_exe_filepath_py + ".exe")
                except OSError as e:
                    Logger.warning(f"Could not clean up temporary files: {e}", AGENT_NAME)
                return True, ""
            else:
                Logger.warning(f"Compilation failed. Return code: {result.returncode}", AGENT_NAME)
                error_message = result.stderr if result.stderr else result.stdout # Some compilers might output to stdout
                Logger.error(f"Compiler errors from {compiler} (in {absolute_src_dir}):\n{error_message}", AGENT_NAME)
                return False, error_message
        except subprocess.TimeoutExpired:
            Logger.error(f"Compilation timed out in {absolute_src_dir}.", AGENT_NAME)
            return False, f"Compilation timed out after 60 seconds in {absolute_src_dir}."
        except FileNotFoundError:
            Logger.error(f"Compiler '{compiler}' not found. Ensure it's in your PATH (especially for Cygwin environment).", AGENT_NAME)
            return False, f"Compiler '{compiler}' not found. Please install it or check your PATH."
        except Exception as e:
            Logger.error(f"An unexpected error occurred during compilation in {absolute_src_dir}: {e}", AGENT_NAME)
            # Best effort to clean up the .c file if process crashes before normal cleanup
            if os.path.exists(temp_c_filepath_py):
                try:
                    os.remove(temp_c_filepath_py)
                except OSError:
                    pass # Ignore cleanup error during an existing error
            return False, f"Unexpected compilation error in {absolute_src_dir}: {e}"