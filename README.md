# Multi-Agent C Code Parallelizer

This project implements a **local multi-agent system in Python** to automatically parallelize C programs using **OpenMP** or **MPI**. Each agent in the system is a component powered by an **LLM** (Groq API) to analyze, transform, and improve the code iteratively until compilation succeeds.

## Project Structure

```
paragineers/
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py       # Main orchestrator agent
│   ├── omp_expert.py         # OpenMP expert agent
│   ├── mpi_expert.py         # MPI expert agent
│   └── checker.py            # Compilation checker agent
├── groq_client.py            # Wrapper for Groq LLM API calls
├── main.py                   # Entry point: reads code and runs orchestrator
├── utils.py                  # File I/O and utility functions
├── examples/
│   └── matrix_mul.c          # Example C source file to parallelize
├── results/
│   └── output.c              # Final parallelized C file (auto-saved)
├── .env                      # Contains GROQ_API_KEY (not committed)
├── .gitignore
└── README.md
```

## Features

* 🔁 Modular agents: orchestrator, OMP expert, MPI expert, and checker.
* 💬 LLM-based code transformation using Groq's `llama3-8b-8192` model.
* 🔍 Heuristic-based expert selection (OMP or MPI).
* 🔧 Compilation checker with retry and refinement loop.
* 🧠 Feedback loop: if compilation fails, the LLM retries with errors as context.

## Requirements

* Python 3.8+
* GCC or MPICC installed
* Groq API key (for LLM access)

### Python packages

Install dependencies:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
groq
python-dotenv
langchain-groq
```

## Setup

1. **Groq API Key**
   Create a `.env` file in the root directory:

   ```
   GROQ_API_KEY=your_groq_key_here
   ```

2. **Verify compilers**
   Ensure you have the compilers installed:

   ```bash
   gcc --version
   mpicc --version
   ```

## Usage

### Basic Usage

```bash
python main.py examples/matrix_mul.c
```

### Advanced Usage with Complex Project Structure

For complex projects like PolyBench with multiple source files and include directories:

```bash
python main.py path/to/target_file.c -p /path/to/project/root -i utilities linear-algebra/blas/gemm -f utilities/polybench.c -c -DPOLYBENCH_TIME -DEXTRALARGE_DATASET
```

### Command-Line Arguments

- `source_file`: Path to the C source file to parallelize (**required**)
- `-p, --project-dir`: Root directory of the C project (default: source file's directory)
- `-i, --include-dirs`: Include directories (relative to project dir)
- `-f, --extra-files`: Additional C files to compile
- `-c, --compiler-flags`: Additional compiler flags

### Example with PolyBench

```bash
# From the PolyBenchC-4.2.1-master directory:
python /path/to/paragineers/main.py linear-algebra/blas/gemm/gemm.c \
  -p . \
  -i utilities linear-algebra/blas/gemm \
  -f utilities/polybench.c \
  -c -DPOLYBENCH_TIME -DEXTRALARGE_DATASET
```

This will:
1. Parallelize the gemm.c file
2. Use the PolyBenchC-4.2.1-master directory as the project root
3. Include the utilities and gemm directories
4. Also compile polybench.c along with the parallelized code
5. Add the -DPOLYBENCH_TIME and -DEXTRALARGE_DATASET flags

## Output

If successful, the parallelized code will be saved to:

```
results/output_<filename>_<timestamp>.c
```

## Agents Overview

| Agent        | Description                                    |
| ------------ | ---------------------------------------------- |
| Orchestrator | Manages flow, expert choice, retries           |
| OMP Expert   | Adds `#pragma omp parallel for` using an LLM   |
| MPI Expert   | Adds MPI setup and communication using an LLM  |
| Checker      | Compiles C code, returns errors if build fails |

## Notes

* The orchestrator uses a retry loop with error feedback to fix generated code.
* OpenMP is used by default unless MPI is explicitly detected or requested.
* This is a research/prototype tool — not production-grade.

## License

MIT License.