"""Advanced JSSP features: Multi-objective, Dynamic Scheduling."""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from copy import deepcopy
from src.data import JSSPInstance, JSSPSchedule


@dataclass
class JSSPInstanceWithDueDates:
    """JSSP instance with due dates for tardiness calculation."""
    instance: JSSPInstance
    due_dates: Dict[int, int]  # job_id -> due_date
    
    def __post_init__(self):
        """Validate due dates."""
        if len(self.due_dates) != self.instance.num_jobs:
            raise ValueError("Due date for each job required")


@dataclass
class MultiObjectiveSchedule:
    """Schedule with multiple objectives."""
    schedule: JSSPSchedule
    makespan: int
    total_tardiness: int  # sum of max(0, completion_time - due_date)
    max_tardiness: int    # max tardiness across jobs
    weighted_score: float  # w1*makespan + w2*tardiness


class MultiObjectiveOptimizer:
    """Multi-objective JSSP solver (makespan + tardiness)."""
    
    def __init__(self, makespan_weight: float = 0.7, tardiness_weight: float = 0.3):
        """
        Initialize multi-objective optimizer.
        
        Args:
            makespan_weight: Weight for makespan (0-1)
            tardiness_weight: Weight for tardiness (0-1)
        """
        if abs(makespan_weight + tardiness_weight - 1.0) > 1e-6:
            raise ValueError("Weights must sum to 1.0")
        
        self.w_makespan = makespan_weight
        self.w_tardiness = tardiness_weight
    
    def solve(
        self,
        instance: JSSPInstanceWithDueDates,
        solver_class
    ) -> MultiObjectiveSchedule:
        """
        Solve using given solver and calculate tardiness.
        
        Args:
            instance: JSSP with due dates
            solver_class: Solver to use (SPT, LPT, GA, CP-SAT, etc.)
        
        Returns:
            MultiObjectiveSchedule with both objectives
        """
        # Solve normally
        solver = solver_class()
        schedule = solver.solve(instance.instance)
        
        # Calculate tardiness metrics
        total_tardiness = 0
        max_tardiness = 0
        
        for job_id in range(instance.instance.num_jobs):
            # Get completion time of last operation in job
            last_op_idx = len(instance.instance.jobs[job_id]) - 1
            completion_time = schedule.end_times.get((job_id, last_op_idx), 0)
            
            due_date = instance.due_dates[job_id]
            tardiness = max(0, completion_time - due_date)
            
            total_tardiness += tardiness
            max_tardiness = max(max_tardiness, tardiness)
        
        # Normalize and compute weighted score
        # Normalize makespan to 0-1 range (use instance total proc time as reference)
        lower_bound = instance.instance.get_total_processing_time()
        normalized_makespan = schedule.makespan / (2 * lower_bound)  # Assume worst case is 2x
        
        # Normalize tardiness to 0-1 range
        max_possible_tardiness = instance.instance.get_total_processing_time()
        normalized_tardiness = total_tardiness / max(1, max_possible_tardiness)
        
        weighted_score = (
            self.w_makespan * normalized_makespan +
            self.w_tardiness * normalized_tardiness
        )
        
        return MultiObjectiveSchedule(
            schedule=schedule,
            makespan=schedule.makespan,
            total_tardiness=total_tardiness,
            max_tardiness=max_tardiness,
            weighted_score=weighted_score
        )
    
    def compute_pareto_frontier(
        self,
        instance: JSSPInstanceWithDueDates,
        solver_class,
        num_runs: int = 10
    ) -> List[MultiObjectiveSchedule]:
        """
        Generate Pareto frontier (approximate).
        
        Runs solver multiple times with different weights to find diverse solutions.
        
        Args:
            instance: JSSP with due dates
            solver_class: Solver to use
            num_runs: Number of runs with different weight combinations
        
        Returns:
            List of non-dominated solutions
        """
        solutions = []
        
        # Try different weight combinations
        for i in range(num_runs):
            # Vary weights
            w_makespan = i / num_runs
            w_tardiness = 1 - w_makespan
            
            optimizer = MultiObjectiveOptimizer(w_makespan, w_tardiness)
            solution = optimizer.solve(instance, solver_class)
            solutions.append(solution)
        
        # Filter to non-dominated solutions
        pareto = []
        for sol in solutions:
            dominated = False
            for other in solutions:
                if (other.makespan <= sol.makespan and 
                    other.total_tardiness <= sol.total_tardiness and
                    (other.makespan < sol.makespan or 
                     other.total_tardiness < sol.total_tardiness)):
                    dominated = True
                    break
            
            if not dominated:
                # Check if not already in pareto
                is_duplicate = any(
                    p.makespan == sol.makespan and 
                    p.total_tardiness == sol.total_tardiness
                    for p in pareto
                )
                if not is_duplicate:
                    pareto.append(sol)
        
        return sorted(pareto, key=lambda x: x.weighted_score)


class DynamicScheduler:
    """Handle dynamic scheduling with machine breakdowns."""
    
    def __init__(self, solver_class):
        """
        Initialize dynamic scheduler.
        
        Args:
            solver_class: Solver to use for re-planning
        """
        self.solver_class = solver_class
    
    def simulate_machine_failure(
        self,
        instance: JSSPInstance,
        schedule: JSSPSchedule,
        failed_machine_id: int,
        failure_time: int
    ) -> Tuple[JSSPSchedule, Dict]:
        """
        Simulate machine failure and re-plan remaining operations.
        
        Args:
            instance: Original JSSP instance
            schedule: Original schedule
            failed_machine_id: Machine that goes down
            failure_time: Time when machine fails
        
        Returns:
            Tuple of (new_schedule, impact_analysis)
        """
        # Identify affected operations (scheduled after failure_time on failed machine)
        affected_ops = []
        unaffected_ops = set()
        
        for (job_id, op_idx), start_time in schedule.start_times.items():
            end_time = schedule.end_times[(job_id, op_idx)]
            machine_id = instance.jobs[job_id][op_idx][0]
            
            if machine_id == failed_machine_id and start_time >= failure_time:
                affected_ops.append((job_id, op_idx))
            else:
                unaffected_ops.add((job_id, op_idx))
        
        # Build partial schedule with unaffected operations fixed
        job_earliest_available = {}
        machine_earliest_available = {}
        
        for (job_id, op_idx), end_time in schedule.end_times.items():
            if (job_id, op_idx) in unaffected_ops:
                job_earliest_available[job_id] = max(
                    job_earliest_available.get(job_id, 0),
                    end_time
                )
                
                machine_id = instance.jobs[job_id][op_idx][0]
                machine_earliest_available[machine_id] = max(
                    machine_earliest_available.get(machine_id, 0),
                    end_time
                )
        
        # Re-solve for affected operations
        start_times = {}
        end_times = {}
        machine_schedule = {m: [] for m in range(instance.num_machines)}
        
        # Copy unaffected operations
        for (job_id, op_idx) in unaffected_ops:
            start_times[(job_id, op_idx)] = schedule.start_times[(job_id, op_idx)]
            end_times[(job_id, op_idx)] = schedule.end_times[(job_id, op_idx)]
            
            machine_id = instance.jobs[job_id][op_idx][0]
            start_t = schedule.start_times[(job_id, op_idx)]
            end_t = schedule.end_times[(job_id, op_idx)]
            machine_schedule[machine_id].append((job_id, op_idx, start_t, end_t))
        
        # Schedule affected operations (greedy: LPT-like)
        job_available = {}
        machine_available = {}
        
        for job_id in range(instance.num_jobs):
            job_available[job_id] = job_earliest_available.get(job_id, 0)
        
        for machine_id in range(instance.num_machines):
            machine_available[machine_id] = machine_earliest_available.get(machine_id, 0)
        
        # Sort affected ops by processing time (LPT heuristic)
        affected_ops.sort(
            key=lambda op: instance.jobs[op[0]][op[1]][1],
            reverse=True
        )
        
        for job_id, op_idx in affected_ops:
            machine_id, proc_time = instance.jobs[job_id][op_idx]
            
            # Special handling: if same machine that failed, delay start
            if machine_id == failed_machine_id:
                # Machine needs recovery time (assume 10 units)
                recovery_time = failure_time + 10
                start_t = max(
                    job_available[job_id],
                    max(recovery_time, machine_available[machine_id])
                )
            else:
                start_t = max(job_available[job_id], machine_available[machine_id])
            
            end_t = start_t + proc_time
            
            start_times[(job_id, op_idx)] = start_t
            end_times[(job_id, op_idx)] = end_t
            job_available[job_id] = end_t
            machine_available[machine_id] = end_t
            machine_schedule[machine_id].append((job_id, op_idx, start_t, end_t))
        
        new_makespan = max(machine_available.values())
        
        new_schedule = JSSPSchedule(
            start_times=start_times,
            end_times=end_times,
            machine_schedule=machine_schedule,
            makespan=new_makespan,
            feasible=True,
            metadata={
                "method": "Dynamic Re-planning",
                "failure": f"Machine {failed_machine_id} at time {failure_time}",
                "recovery_time": 10
            }
        )
        
        # Impact analysis
        impact = {
            "original_makespan": schedule.makespan,
            "new_makespan": new_makespan,
            "makespan_increase": new_makespan - schedule.makespan,
            "makespan_increase_pct": (new_makespan - schedule.makespan) / schedule.makespan * 100,
            "affected_operations": len(affected_ops),
            "failed_machine": failed_machine_id,
            "failure_time": failure_time
        }
        
        return new_schedule, impact
    
    def analyze_schedule_robustness(
        self,
        instance: JSSPInstance,
        schedule: JSSPSchedule,
        machine_id: int,
        failure_window_start: int,
        failure_window_end: int,
        step: int = 1
    ) -> List[Dict]:
        """
        Analyze robustness by simulating failures at different times.
        
        Args:
            instance: JSSP instance
            schedule: Original schedule
            machine_id: Machine to simulate failures on
            failure_window_start: Start time for simulation
            failure_window_end: End time for simulation
            step: Time step for simulation
        
        Returns:
            List of impact analyses at different failure times
        """
        results = []
        
        for failure_time in range(failure_window_start, failure_window_end, step):
            _, impact = self.simulate_machine_failure(
                instance, schedule, machine_id, failure_time
            )
            results.append(impact)
        
        return results
