class Config:
    """Static configuration settings."""
    MODEL_NAME =            "llama-3.1-8b-instant"
    MAX_RETRIES =           3
    TEMP =                  0.0
    MAX_TOKENS =            None

    OMP_PROCESS_PROMPT =    "// Add OpenMP pragmas:\n"
    OMP_REFINE_PROMPT =     "// Please adjust OpenMP pragmas:\n"

    MPI_PROCESS_PROMPT =    "// Add MPI boilerplate:\n"
    MPI_REFINE_PROMPT =     "// Fix MPI usage:\n"