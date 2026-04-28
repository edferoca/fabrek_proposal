"""Evaluation utilities for JSSP solutions."""
from typing import Dict, Tuple
import time
from src.data import JSSPInstance, JSSPSchedule


def evaluate_schedule(
    instance: JSSPInstance,
    schedule: JSSPSchedule,
    computation_time: float = 0.0
) -> Dict:
    """
    Evaluate a schedule solution.
    
    Args:
        instance: The JSSP instance.
        schedule: The proposed schedule.
        computation_time: Time taken to compute the schedule.
    
    Returns:
        Dictionary with evaluation metrics.
    """
    metrics = {
        "makespan": schedule.makespan,
        "feasible": schedule.feasible,
        "computation_time": computation_time,
        "instance": str(instance),
    }
    
    if schedule.feasible:
        # Additional metrics for feasible solutions
        lower_bound = instance.get_total_processing_time()
        metrics["lower_bound"] = lower_bound
        metrics["optimality_gap"] = (schedule.makespan - lower_bound) / lower_bound * 100
    
    return metrics


def calculate_metrics(
    instance: JSSPInstance,
    schedules: Dict[str, JSSPSchedule],
    computation_times: Dict[str, float] = None
) -> Dict:
    """
    Calculate comparison metrics for multiple schedules.
    
    Args:
        instance: The JSSP instance.
        schedules: Dictionary of method_name -> schedule.
        computation_times: Dictionary of method_name -> computation_time.
    
    Returns:
        Dictionary with comparative metrics.
    """
    if computation_times is None:
        computation_times = {k: 0.0 for k in schedules}
    
    results = {}
    
    for method_name, schedule in schedules.items():
        comp_time = computation_times.get(method_name, 0.0)
        results[method_name] = evaluate_schedule(
            instance, schedule, comp_time
        )
    
    # Find best makespan
    feasible_methods = {
        k: v for k, v in results.items() if v["feasible"]
    }
    
    if feasible_methods:
        best_makespan = min(v["makespan"] for v in feasible_methods.values())
        results["best_makespan"] = best_makespan
        
        for method_name in feasible_methods:
            results[method_name]["gap_from_best"] = (
                results[method_name]["makespan"] - best_makespan
            ) / best_makespan * 100
    
    return results


def is_feasible_schedule(
    instance: JSSPInstance,
    start_times: Dict[Tuple[int, int], int],
    end_times: Dict[Tuple[int, int], int]
) -> Tuple[bool, str]:
    """
    Check if a schedule is feasible.
    
    Args:
        instance: The JSSP instance.
        start_times: Dictionary of (job_id, op_index) -> start_time.
        end_times: Dictionary of (job_id, op_index) -> end_time.
    
    Returns:
        Tuple of (is_feasible, error_message).
    """
    # Check precedence constraints
    for job_id, job in enumerate(instance.jobs):
        for op_idx in range(len(job)):
            if op_idx > 0:
                # Operation i must start after operation i-1 ends
                prev_op_key = (job_id, op_idx - 1)
                curr_op_key = (job_id, op_idx)
                
                if end_times.get(prev_op_key, float('inf')) > start_times.get(curr_op_key, float('inf')):
                    return False, f"Precedence violation: job {job_id}"
    
    # Check machine capacity constraints
    machine_operations: Dict[int, list] = {}
    
    for (job_id, op_idx), start_time in start_times.items():
        end_time = end_times.get((job_id, op_idx))
        if end_time is None:
            return False, f"Missing end time for operation ({job_id}, {op_idx})"
        
        machine_id = instance.jobs[job_id][op_idx][0]
        
        if machine_id not in machine_operations:
            machine_operations[machine_id] = []
        
        machine_operations[machine_id].append((start_time, end_time))
    
    # Check for overlaps on machines
    for machine_id, operations in machine_operations.items():
        operations.sort()
        for i in range(len(operations) - 1):
            if operations[i][1] > operations[i + 1][0]:
                return False, f"Machine {machine_id} overlap"
    
    return True, "Schedule is feasible"
