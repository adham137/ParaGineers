import subprocess
import os
from utils import Logger, LogColors # Assuming Logger and LogColors are in utils.py

AGENT_NAME = "Checker"

class Checker:
    def compile(self, code: str, use_openmp: bool, src_dir: str, project_dir: str = None, include_dirs: list = None, 
                extra_files: list = None, extra_flags: list = None):
        """
        Compiles the given C code within a project structure.
        Args:
            code (str): The C code to compile.
            use_openmp (bool): Whether to include OpenMP flags.
            src_dir (str): The directory where the temp C file will be created.
            project_dir (str): The root directory of the C project (compilation runs here).
            include_dirs (list): List of include directories relative to project_dir.
            extra_files (list): List of additional C files to compile (relative to project_dir).
            extra_flags (list): Additional compiler flags.
        Returns:
            tuple: (bool, str) where bool is True on success, False on failure,
                   and str contains error messages if compilation failed.
        """
        
        # If project_dir not provided, use src_dir as fallback
        if not project_dir:
            project_dir = src_dir
        
        # Ensure all paths are absolute for clarity
        absolute_src_dir = os.path.abspath(src_dir)
        absolute_project_dir = os.path.abspath(project_dir)
        
        Logger.info(f"Source directory: {absolute_src_dir}", AGENT_NAME, LogColors.CHECKER)
        Logger.info(f"Project directory: {absolute_project_dir}", AGENT_NAME, LogColors.CHECKER)
        
        # Default values if not provided
        include_dirs = include_dirs or []
        extra_files = extra_files or []
        extra_flags = extra_flags or []

        temp_c_filename = "temp_generated_code.c" # Name for the temporary C file
        temp_exe_filename = "temp_compiled_exe"   # Name for the temporary executable
        
        # Path for the temporary C file (relative to src_dir)
        temp_c_filepath_abs = os.path.join(absolute_src_dir, temp_c_filename)
        # Path for the executable (relative to project_dir)
        temp_exe_filepath_abs = os.path.join(absolute_project_dir, temp_exe_filename)

        Logger.info(f"Attempting to compile code. OpenMP: {use_openmp}", AGENT_NAME, LogColors.CHECKER)
        Logger.debug(f"Writing code to temporary file: {temp_c_filepath_abs}", AGENT_NAME, LogColors.CHECKER)
        
        # Write the modified code to the temporary file
        try:
            with open(temp_c_filepath_abs, "w") as f:
                f.write(code)
        except IOError as e:
            Logger.error(f"Failed to write temporary C file '{temp_c_filepath_abs}': {e}", AGENT_NAME)
            return False, f"IOError: Failed to write temporary file {temp_c_filepath_abs}. Details: {e}"

        # Determine the appropriate compiler
        compiler = "mpicc" if not use_openmp and "MPI_" in code.upper() else "gcc"
        Logger.info(f"Using compiler: {compiler}", AGENT_NAME, LogColors.CHECKER)
        
        # Start building the compilation command
        cmd = [compiler]
        
        # Add -fopenmp flag if using OpenMP
        if use_openmp:
            cmd.append("-fopenmp")
        
        # Add optimization flag
        cmd.append("-O3")
        
        # Add include directories with -I flags
        for include_dir in include_dirs:
            # Make the include path relative to the project directory
            if os.path.isabs(include_dir):
                # If absolute path provided, use as is
                cmd.extend(["-I", include_dir])
            else:
                # If relative path, make it relative to project_dir for the command
                cmd.extend(["-I", include_dir])
        
        # Add any extra files to compile
        for extra_file in extra_files:
            # Make the file path relative to the project directory
            if os.path.isabs(extra_file):
                # If absolute path provided, use as is
                cmd.append(extra_file)
            else:
                # If relative path, keep it relative for the command since cwd will be project_dir
                cmd.append(extra_file)
        
        # Add the temporary C file to compile (make path relative to project_dir)
        temp_c_path_rel_to_project = os.path.relpath(temp_c_filepath_abs, absolute_project_dir)
        cmd.append(temp_c_path_rel_to_project)
        
        # Add extra flags
        cmd.extend(extra_flags)
        
        # Add output file flag
        cmd.extend(["-o", temp_exe_filename])
        
        Logger.info(f"Compilation command: {' '.join(cmd)}", AGENT_NAME, LogColors.CHECKER)
        Logger.info(f"Executing command in directory: {absolute_project_dir}", AGENT_NAME, LogColors.CHECKER)

        try:
            # Execute the compilation command with cwd set to the project directory
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=absolute_project_dir,
                timeout=60 # Timeout after 60 seconds
            )

            if result.returncode == 0:
                Logger.success(f"Compilation successful in {absolute_project_dir}.", AGENT_NAME)
                # Clean up temporary files on success
                try:
                    os.remove(temp_c_filepath_abs)
                    # temp_exe_filepath_abs might have .exe on Windows even under Cygwin if gcc adds it
                    if os.path.exists(temp_exe_filepath_abs):
                        os.remove(temp_exe_filepath_abs)
                    elif os.path.exists(temp_exe_filepath_abs + ".exe"): # Check for .exe extension
                         os.remove(temp_exe_filepath_abs + ".exe")
                except OSError as e:
                    Logger.warning(f"Could not clean up temporary files: {e}", AGENT_NAME)
                return True, ""
            else:
                Logger.warning(f"Compilation failed. Return code: {result.returncode}", AGENT_NAME)
                error_message = result.stderr if result.stderr else result.stdout # Some compilers output to stdout
                Logger.error(f"Compiler errors from {compiler} (in {absolute_project_dir}):\n{error_message}", AGENT_NAME)
                return False, error_message
        except subprocess.TimeoutExpired:
            Logger.error(f"Compilation timed out in {absolute_project_dir}.", AGENT_NAME)
            return False, f"Compilation timed out after 60 seconds in {absolute_project_dir}."
        except FileNotFoundError:
            Logger.error(f"Compiler '{compiler}' not found. Ensure it's in your PATH (especially for Cygwin environment).", AGENT_NAME)
            return False, f"Compiler '{compiler}' not found. Please install it or check your PATH."
        except Exception as e:
            Logger.error(f"An unexpected error occurred during compilation in {absolute_project_dir}: {e}", AGENT_NAME)
            # Best effort to clean up the .c file if process crashes before normal cleanup
            if os.path.exists(temp_c_filepath_abs):
                try:
                    os.remove(temp_c_filepath_abs)
                except OSError:
                    pass # Ignore cleanup error during an existing error
            return False, f"Unexpected compilation error in {absolute_project_dir}: {e}"