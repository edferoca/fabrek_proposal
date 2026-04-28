# JSSP Solver - Job Shop Scheduling Problem

## Overview

This project implements a comprehensive solution to the **Job Shop Scheduling Problem (JSSP)**, a classic combinatorial optimization challenge. The solution combines:

- **Classical baselines**: SPT/LPT dispatching rules, genetic algorithms, and constraint programming
- **ML/LLM approaches**: LLM-augmented scheduling with fallback mechanisms
- **Evaluation & visualization**: Makespan comparison, Gantt charts, and detailed metrics

## Problem Definition

Given:
- A set of **jobs**, each consisting of ordered operations
- Each operation must be processed on a specific **machine**
- Each machine can only process one operation at a time

Find: A schedule that minimizes **makespan** (total completion time) while respecting all constraints.

### Instance Specification

The default instance uses:
- **6 jobs × 6 machines** (36 operations)
- Processing times: 5–15 time units per operation
- Each job visits each machine exactly once in random order

**Rationale for 6×6 size:**
- Small enough to solve quickly (~seconds) on a laptop
- Large enough to show meaningful differences between approaches
- Solvable to optimality or near-optimality with modern solvers
- Suitable for both classical and ML approaches

## Quick Start (< 15 minutes)

### 1. Setup

```bash
# Navigate to project directory
cd fabrek_proposal

# Activate virtual environment (Windows)
.venvfabrek\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Run All Solvers

```bash
python main.py
```

This will:
1. Generate a random 6×6 JSSP instance
2. Solve it using 5 different approaches
3. Print a comparison table
4. Generate a Gantt chart for the best solution
5. Save results to `results/` directory

**Expected output:** Completes in ~20–30 seconds on a modern laptop.

### 3. Interpret Results

```
Method              Makespan    Time (s)    Feasible
---------------------------------------------------
SPT                 156         0.0001      Yes
LPT                 148         0.0002      Yes
GA                  142         0.1234      Yes
CP-SAT              138         1.2345      Yes
LLM                 148         0.0002      Yes
```

- **Makespan**: Total time to complete all jobs (lower is better)
- **Time**: Computation time for finding the solution
- **Feasible**: Whether all constraints are satisfied

## Architecture

### `src/data/`
- `jssp_instance.py`: Core JSSP data structures
- `generators.py`: Random instance generation and benchmark loading

### `src/baselines/`
- `dispatching_rules.py`: SPT and LPT heuristics
- `genetic_algorithm.py`: Population-based metaheuristic
- `cp_sat_solver.py`: Google OR-Tools constraint programming solver

### `src/ml_approaches/`
- `llm_scheduler.py`: LLM-augmented scheduling (with heuristic fallback)

### `src/utils/`
- `evaluation.py`: Metrics, feasibility checking
- `visualization.py`: Gantt charts and comparison plots

## Approaches Explained

### 1. SPT (Shortest Processing Time)
**Type:** Greedy dispatching rule  
**How it works:** Always schedule the next available operation with the shortest processing time  
**Pros:** Extremely fast, simple to understand  
**Cons:** Often suboptimal, ignores future bottlenecks

### 2. LPT (Longest Processing Time)
**Type:** Greedy dispatching rule  
**How it works:** Always schedule the next available operation with the longest processing time  
**Pros:** Fast, better load balancing than SPT  
**Cons:** Still greedy, can be suboptimal

### 3. Genetic Algorithm
**Type:** Evolutionary metaheuristic  
**How it works:**
  - Represents solutions as permutations of operations
  - Uses tournament selection, order crossover, and swap mutation
  - Evolves population over 50 generations
  
**Pros:** Can escape local optima, parallelizable  
**Cons:** Slower than greedy methods, stochastic results

### 4. OR-Tools CP-SAT
**Type:** Constraint programming solver  
**How it works:**
  - Formulates JSSP as integer linear program
  - Uses SAT-based branch-and-cut
  - Guaranteed to find optimal solution (within time limit)
  
**Pros:** Often optimal or near-optimal, robust  
**Cons:** Slower for large instances, requires careful modeling

### 5. LLM-Augmented Scheduler
**Type:** Hybrid AI + heuristic  
**How it works:**
  - Formats JSSP instance as JSON
  - Prompts LLM (e.g., GPT-4) to generate schedule
  - Falls back to LPT if LLM not available
  
**Pros:** Leverages language model reasoning, interpretable  
**Cons:** Dependent on LLM API, cost considerations

## Key Design Decisions & Rationale

| Decision | Why | Alternative | Trade-off |
|----------|-----|-------------|-----------|
| 6×6 instance | Fast, representative | 10×10 or larger | Scalability vs. quick iteration |
| Sequence representation in GA | Standard for JSSP | Direct machine-machine moves | Simplicity vs. expressiveness |
| LPT as LLM fallback | Reliable baseline | Random, SPT | Robustness vs. diversity |
| Separate modules per approach | Maintainability, modularity | Single monolithic file | File count vs. clarity |
| Gantt chart visualization | Industry standard | Heatmaps, tables | Familiarity vs. novelty |

## What Would I Do Differently With More Time?

1. **Advanced ML**: Implement graph neural networks (GNNs) or reinforcement learning (RL) for learned dispatching policies
2. **Warm starting**: Use LLM solutions as initial population for GA / input to CP-SAT
3. **Dynamic scheduling**: Add machine breakdowns mid-schedule and re-planning logic
4. **Multi-objective**: Extend to minimize tardiness + makespan
5. **Microservice integration**: REST API with caching, latency SLAs, load testing
6. **Hyperparameter tuning**: Bayesian optimization for GA parameters
7. **Benchmark validation**: Test on OR-Library instances, compare to known optima
8. **Production logging**: Structured logging, metrics tracking, model monitoring

## AI Assistance Summary

### Used As Tools:
- **Code generation**: Baseline solvers, data structures, plotting
- **Debugging**: Type hints, edge cases, validation logic
- **Documentation**: README structure, docstrings

### Written From Scratch:
- Problem formulation and constraints
- Core GA implementation (logic, operators)
- Evaluation metrics and comparison framework
- Project structure and module organization

### Rationale:
- AI excelled at boilerplate and scaffolding
- Human oversight crucial for algorithm correctness and problem understanding
- Hybrid approach maximized productivity while maintaining rigor

## How to Reproduce Results

On a Windows laptop with Python 3.10+:

```bash
# 1. Clone/navigate to project
cd fabrek_proposal

# 2. Create and activate venv (if not already done)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the benchmark
python main.py

# 5. View results in results/ directory
```

**Total time:** ~5 minutes setup, ~30 seconds execution

## Integration as Production Microservice

### API Contract
```python
POST /api/jssp/solve
{
    "jobs": [[{"machine": 0, "duration": 5}, ...], ...],
    "solver": "cp-sat",  # "spt", "lpt", "ga", "cp-sat", "llm"
    "timeout": 30
}

Response:
{
    "makespan": 142,
    "schedule": {...},
    "computation_time": 1.234,
    "feasible": true
}
```

### Latency Requirements
- **SPT/LPT**: < 10 ms (trivial heuristics)
- **GA**: 100–500 ms (configurable generations)
- **CP-SAT**: 1–10 s (configurable time limit)

### Production Considerations
- **Caching**: Memoize solutions for identical instances
- **Load balancing**: Distribute GA/CP-SAT across workers
- **Monitoring**: Track solve times, feasibility rate, optimality gap
- **Fallback**: If primary solver times out, return greedy solution

## Files & Directory Structure

```
fabrek_proposal/
├── src/
│   ├── data/
│   │   ├── jssp_instance.py
│   │   └── generators.py
│   ├── baselines/
│   │   ├── dispatching_rules.py
│   │   ├── genetic_algorithm.py
│   │   └── cp_sat_solver.py
│   ├── ml_approaches/
│   │   └── llm_scheduler.py
│   └── utils/
│       ├── evaluation.py
│       └── visualization.py
├── results/           # Output directory for Gantt charts, metrics
├── main.py            # Entry point
├── requirements.txt   # Dependencies
├── README.md          # This file
└── prompts.md         # LLM interaction log
```

## Testing & Validation

All solutions are validated for:
- **Precedence constraints**: Operations within a job respect order
- **Capacity constraints**: Machines process at most one operation at a time
- **Completeness**: All operations are scheduled

## References

- [Google OR-Tools Docs](https://developers.google.com/optimization/cp-sat)
- [JSSP Overview](https://en.wikipedia.org/wiki/Job_shop_scheduling)
- [OR-Library Benchmarks](http://people.brunel.ac.uk/~mastjjb/jeb/orlib/jssp.html)

---

**Status:** ✓ Ready for review  
**Last Updated:** 2024  
**Contact:** edferoca
