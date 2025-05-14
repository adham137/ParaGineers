## 📂 Project Structure

```
parallelizer/
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

---

## 🧠 Multi-Agent C Code Parallelizer

This project implements a **local multi-agent system in Python** to automatically parallelize C programs using **OpenMP** or **MPI**. Each agent in the system is a component powered by an **LLM** (Groq API) to analyze, transform, and improve the code iteratively until compilation succeeds.

### ✨ Features

* 🔁 Modular agents: orchestrator, OMP expert, MPI expert, and checker.
* 💬 LLM-based code transformation using Groq's `llama3-8b-8192` model.
* 🔍 Heuristic-based expert selection (OMP or MPI).
* 🔧 Compilation checker with retry and refinement loop.
* 🧠 Feedback loop: if compilation fails, the LLM retries with errors as context.

---

## 🚀 How It Works

1. **Input**: Provide a `.c` file (e.g., `examples/matrix_mul.c`).
2. **Agent Flow**:

   * Orchestrator selects the best expert (OMP or MPI).
   * Expert sends the code to an LLM to insert parallel directives.
   * Checker compiles the output using `gcc` or `mpicc`.
   * If failed, the expert tries again with error feedback.
3. **Output**: A parallelized, compilable `.c` file saved in `results/output.c`.

---

## 🛠 Requirements

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
```

---

## 🔐 Setup

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

---

## 🧪 Usage

From the root folder:

```bash
python main.py examples/matrix_mul.c
```

If successful, the modified parallelized code will be saved to:

```
results/output.c
```

---

## 🧩 Agents Overview

| Agent        | Description                                    |
| ------------ | ---------------------------------------------- |
| Orchestrator | Manages flow, expert choice, retries           |
| OMP Expert   | Adds `#pragma omp parallel for` using an LLM   |
| MPI Expert   | Adds MPI setup and communication using an LLM  |
| Checker      | Compiles C code, returns errors if build fails |

---

## 📁 Example C Input

```c
// examples/matrix_mul.c

void multiply(int a[10][10], int b[10][10], int c[10][10]) {
    for (int i = 0; i < 10; i++)
        for (int j = 0; j < 10; j++) {
            c[i][j] = 0;
            for (int k = 0; k < 10; k++)
                c[i][j] += a[i][k] * b[k][j];
        }
}
```

After processing, it may be annotated with:

```c
#pragma omp parallel for
for (int i = 0; i < 10; i++)
```

Or turned into a distributed MPI version.

---

## 📌 Notes

* The orchestrator uses a retry loop with error feedback to fix generated code.
* OpenMP is used by default unless MPI is explicitly detected or requested.
* This is a research/prototype tool — not production-grade.

---

## 📄 License

MIT License.

---

