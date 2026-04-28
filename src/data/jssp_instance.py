"""Core JSSP data structures."""
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Operation:
    """Represents a single operation in a job."""
    job_id: int
    operation_index: int
    machine_id: int
    processing_time: int


@dataclass
class JSSPSchedule:
    """Represents a solution to the JSSP."""
    start_times: dict  # (job_id, op_index) -> start_time
    end_times: dict    # (job_id, op_index) -> end_time
    machine_schedule: dict  # machine_id -> list of (job_id, op_index, start, end)
    makespan: int
    feasible: bool
    metadata: dict = None


class JSSPInstance:
    """Represents a Job Shop Scheduling Problem instance."""
    
    def __init__(self, jobs: List[List[Tuple[int, int]]], name: str = "jssp"):
        """
        Initialize JSSP instance.
        
        Args:
            jobs: List of jobs. Each job is a list of (machine_id, processing_time) tuples.
            name: Name of the instance.
        """
        self.name = name
        self.jobs = jobs
        self.num_jobs = len(jobs)
        self.num_machines = max(max(m for m, _ in job) for job in jobs) + 1
        self.num_operations = sum(len(job) for job in jobs)
        
        # Validate instance
        self._validate()
    
    def _validate(self):
        """Validate the JSSP instance."""
        if not self.jobs:
            raise ValueError("JSSP instance must have at least one job")
        
        for job_id, job in enumerate(self.jobs):
            if not job:
                raise ValueError(f"Job {job_id} has no operations")
            for machine_id, proc_time in job:
                if machine_id < 0 or machine_id >= self.num_machines:
                    raise ValueError(f"Invalid machine ID {machine_id} in job {job_id}")
                if proc_time <= 0:
                    raise ValueError(f"Processing time must be positive in job {job_id}")
    
    def get_job_operations(self, job_id: int) -> List[Operation]:
        """Get all operations for a job."""
        operations = []
        for op_idx, (machine_id, proc_time) in enumerate(self.jobs[job_id]):
            operations.append(Operation(job_id, op_idx, machine_id, proc_time))
        return operations
    
    def get_total_processing_time(self) -> int:
        """Get total processing time across all jobs."""
        return sum(proc_time for job in self.jobs for _, proc_time in job)
    
    def to_dict(self) -> dict:
        """Convert instance to dictionary."""
        return {
            "name": self.name,
            "num_jobs": self.num_jobs,
            "num_machines": self.num_machines,
            "num_operations": self.num_operations,
            "jobs": self.jobs
        }
    
    def __repr__(self) -> str:
        return f"JSSP({self.num_jobs}j×{self.num_machines}m, {self.num_operations} ops)"
