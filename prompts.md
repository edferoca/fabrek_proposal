# Use and Implementation of AI Assistants & LLM Tools

This project was carried out largely with the help of AI assistants. In light of this, the following outlines the different decisions and reasoning that led to the implementation of each prompt and request used to build this project.

## Motivation 1: Structuring

### Context:
- Lack of understanding regarding the proper interpretation of certain contexts, such as JSSP problems in their practical deployment
- Limited time to refine existing knowledge and apply it to the problem

### Prompts Used

- "Explain how JSSP problems work, what methods are typically used to solve them, and where ML or LLM models fit in"

### Tools Used
- ChatGPT Pro

### Decisions Made
- A contextual framework was created to better understand and build a mental model of the requirements involved in deploying solutions for these types of problems
- A basic project structure was designed as a mental map:


project/
│
├── results/
│
├── src/
│ ├── data/ → Definition of the JSSP problem (e.g., 6×6)
│ ├── baselines/ → Classical methods
│ ├── ml-LLM_impl/ → AI-based methods
│ ├── comparation/ → Method comparison
│ ├── visualization/ → Functions for Gantt chart visualization
│ ├── main.py → Run the full pipeline


---

## Motivation 2: Implementation

### Context:
- Motivation to use new AI assistant tools such as VS Code Copilot
- Limited time to refine existing knowledge and apply it to the problem

### Prompts Used

- "Structure a project based on this statement: Job Shop Scheduling. Estimated effort: given a set of jobs, each consisting of ordered operations that must be processed on specific machines, find a schedule that minimises makespan (total completion time). Build a pipeline that takes a JSSP instance (jobs × machines × processing times) and produces a feasible, high-quality schedule. Generate random instances programmatically — start small (e.g., 6 jobs × 6 machines) and create a way to scale up to show how your approach behaves. Assume the following requirements:

- Python 3.10+. Any libraries are acceptable (Google OR-Tools, PyTorch, scikit-learn, custom code — your choice).
- At least one classical/heuristic baseline (e.g., dispatching rule like SPT/LPT, genetic algorithm, or constraint programming via Google OR-Tools CP-SAT solver).
- At least one ML or LLM-augmented approach (choose one or combine).
- Provide a comparison: makespan, feasibility rate, computation time. Show where each approach succeeds and fails.
- Visualization of at least one schedule (Gantt chart or equivalent)."

### Tools Used
- VS Code Copilot (Claude Haiku 4.5)

### Decisions Made
- The assistant structured the entire project, including modified folders and ready-to-run files
- A first visual inspection of all generated components was performed, followed by:
  - Creation of the virtual environment and installation of dependencies
  - Execution of `python main.py`
- Execution errors and unused functions were identified:
  - Some were fixed manually by following terminal outputs
  - Others were passed back to the assistant for correction