"""Generators for JSSP instances."""
import numpy as np
from typing import Tuple, Optional

from .jssp_instance import JSSPInstance


def generate_random_jssp(
    num_jobs: int,
    num_machines: int,
    min_proc_time: int = 1,
    max_proc_time: int = 10,
    seed: Optional[int] = None
) -> JSSPInstance:
    """
    Generate a random JSSP instance.
    
    Args:
        num_jobs: Number of jobs.
        num_machines: Number of machines.
        min_proc_time: Minimum processing time.
        max_proc_time: Maximum processing time.
        seed: Random seed for reproducibility.
    
    Returns:
        JSSPInstance: A random JSSP instance.
    """
    if seed is not None:
        np.random.seed(seed)
    
    jobs = []
    for job_id in range(num_jobs):
        # Each job visits each machine exactly once in random order
        machines = np.random.permutation(num_machines)
        job = []
        for machine_id in machines:
            proc_time = np.random.randint(min_proc_time, max_proc_time + 1)
            job.append((int(machine_id), int(proc_time)))
        jobs.append(job)
    
    return JSSPInstance(
        jobs=jobs,
        name=f"random_{num_jobs}j_{num_machines}m"
    )


def load_benchmark_instance(filename: str) -> JSSPInstance:
    """
    Load a benchmark JSSP instance from file (OR-Library format).
    
    Args:
        filename: Path to the benchmark file.
    
    Returns:
        JSSPInstance: The loaded instance.
    """
    jobs = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Skip header lines
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        parts = list(map(int, line.split()))
        if len(parts) < 2:
            continue
        
        # Format: machine_1 proc_time_1 machine_2 proc_time_2 ...
        job = []
        for i in range(0, len(parts), 2):
            machine_id = parts[i] - 1  # Convert to 0-indexed
            proc_time = parts[i + 1]
            job.append((machine_id, proc_time))
        
        if job:
            jobs.append(job)
    
    return JSSPInstance(jobs=jobs, name=f"benchmark_{len(jobs)}j")
