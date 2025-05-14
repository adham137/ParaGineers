class Config:
    """Static configuration settings."""
    MODEL_NAME = "llama-3.3-70b-versatile"  
    MAX_RETRIES = 3
    TEMP = 0.1  
    MAX_TOKENS = 2048 

    # --- Prompts ---
    # System-level instruction (optional, can be pre-pended by the agent)
    SYSTEM_ROLE_C_PARALLELIZER = (
        "You are an expert C programmer specialized in code parallelization. "
        "Your goal is to modify the given C code to make it run efficiently in parallel. "
        "Ensure the modified code is complete, correct, and compilable. "
        "Only output the complete, modified C code. Do not include any explanations, apologies, or extraneous text. "
        "Preserve all existing functionality and comments unless directly related to parallelization changes."
    )

    # --- OpenMP Prompts ---
    OMP_PROCESS_PROMPT_TEMPLATE = (
        f"{SYSTEM_ROLE_C_PARALLELIZER}\n"
        "The following C code needs to be parallelized using OpenMP.\n"
        "Identify the most suitable loops (typically the outermost loops with independent iterations or those with significant computation) "
        "for parallelization using '#pragma omp parallel for'.\n"
        "Consider data sharing clauses (shared, private, reduction) carefully to ensure correctness.\n"
        "Add necessary OpenMP headers like `<omp.h>` if not present.\n"
        "Here is the C code:\n"
        "```c\n"
        "{code}\n"
        "```\n"
        "Return only the complete, modified C code with OpenMP directives."
    )

    OMP_REFINE_PROMPT_TEMPLATE = (
        f"{SYSTEM_ROLE_C_PARALLELIZER}\n"
        "The previous attempt to parallelize the C code with OpenMP resulted in compilation errors or runtime issues.\n"
        "Original C Code:\n"
        "```c\n"
        "{original_code}\n"
        "```\n"
        "Attempted OpenMP Code:\n"
        "```c\n"
        "{attempted_code}\n"
        "```\n"
        "Compilation/Runtime Errors:\n"
        "```\n"
        "{errors}\n"
        "```\n"
        "Please analyze the errors and the attempted code. Adjust the OpenMP pragmas, data sharing clauses (shared, private, firstprivate, lastprivate, reduction), "
        "loop scheduling, or other necessary aspects to fix the issues.\n"
        "Ensure that the fundamental logic of the original code remains unchanged.\n"
        "Return only the complete, corrected, and compilable C code with OpenMP directives."
    )

    # --- MPI Prompts ---
    MPI_PROCESS_PROMPT_TEMPLATE = (
        f"{SYSTEM_ROLE_C_PARALLELIZER}\n"
        "The following C code needs to be parallelized using MPI.\n"
        "This typically involves:\n"
        "1. Adding MPI headers like `<mpi.h>`.\n"
        "2. Initializing and finalizing the MPI environment (MPI_Init, MPI_Finalize).\n"
        "3. Getting rank and size (MPI_Comm_rank, MPI_Comm_size).\n"
        "4. Distributing data among processes (e.g., scattering input arrays).\n"
        "5. Dividing work among processes (e.g., each process handles a portion of a loop).\n"
        "6. Gathering results from processes (e.g., gathering computed parts of an array).\n"
        "7. Using appropriate MPI communication functions (MPI_Send, MPI_Recv, MPI_Bcast, MPI_Scatter, MPI_Gather, MPI_Reduce, etc.).\n"
        "Focus on parallelizing the main computational loops.\n"
        "Here is the C code:\n"
        "```c\n"
        "{code}\n"
        "```\n"
        "Return only the complete, modified C code with MPI parallelization."
    )

    MPI_REFINE_PROMPT_TEMPLATE = (
        f"{SYSTEM_ROLE_C_PARALLELIZER}\n"
        "The previous attempt to parallelize the C code with MPI resulted in compilation errors or runtime issues.\n"
        "Original C Code:\n"
        "```c\n"
        "{original_code}\n"
        "```\n"
        "Attempted MPI Code:\n"
        "```c\n"
        "{attempted_code}\n"
        "```\n"
        "Compilation/Runtime Errors:\n"
        "```\n"
        "{errors}\n"
        "```\n"
        "Please analyze the errors and the attempted code. Correct the MPI setup, data distribution, work division, communication patterns, or any other MPI-related issues.\n"
        "Pay close attention to buffer sizes, data types, tags, and communicator arguments in MPI calls.\n"
        "Ensure that the fundamental logic of the original code remains unchanged.\n"
        "Return only the complete, corrected, and compilable C code with MPI parallelization."
    )