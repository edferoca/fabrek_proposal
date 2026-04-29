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

# Create virtual environment
python -m venv .venv

# Activate — Linux/macOS:
source .venv/bin/activate
# Activate — Windows (PowerShell):
# .venv\Scripts\Activate.ps1

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


## How to Reproduce Results

```bash
# 1. Navigate to project
cd fabrek_proposal

# 2. Create and activate venv
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\Activate.ps1    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the benchmark
python main.py

# 5. View results in results/ directory
```


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
