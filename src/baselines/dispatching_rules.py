"""Dispatching rule-based solvers."""
from typing import Dict, Tuple, List
from src.data import JSSPInstance, JSSPSchedule


class DispatchingRuleSolver:
    """Base class for dispatching rule solvers."""
    
    def __init__(self, rule_name: str):
        self.rule_name = rule_name
    
    def solve(self, instance: JSSPInstance) -> JSSPSchedule:
        """Solve using the dispatching rule."""
        # Track earliest available time for each job and machine
        job_available_time = [0] * instance.num_jobs
        machine_available_time = [0] * instance.num_machines
        
        start_times = {}
        end_times = {}
        machine_schedule = {m: [] for m in range(instance.num_machines)}
        
        # Queue of available operations (job_id, op_idx)
        available_ops = [(job_id, 0) for job_id in range(instance.num_jobs)]
        completed = set()
        
        while available_ops:
            # Select operation using dispatching rule
            selected = self._select_operation(available_ops, instance, job_available_time)
            job_id, op_idx = selected
            
            # Schedule the operation
            machine_id, proc_time = instance.jobs[job_id][op_idx]
            
            # Start time is max of job and machine availability
            start_time = max(job_available_time[job_id], machine_available_time[machine_id])
            end_time = start_time + proc_time
            
            # Record schedule
            start_times[(job_id, op_idx)] = start_time
            end_times[(job_id, op_idx)] = end_time
            job_available_time[job_id] = end_time
            machine_available_time[machine_id] = end_time
            machine_schedule[machine_id].append((job_id, op_idx, start_time, end_time))
            
            # Remove from available and mark as completed
            available_ops.remove(selected)
            completed.add(selected)
            
            # Add next operation of this job if exists
            if op_idx + 1 < len(instance.jobs[job_id]):
                available_ops.append((job_id, op_idx + 1))
        
        # Calculate makespan
        makespan = max(machine_available_time)
        
        return JSSPSchedule(
            start_times=start_times,
            end_times=end_times,
            machine_schedule=machine_schedule,
            makespan=makespan,
            feasible=True,
            metadata={"rule": self.rule_name}
        )
    
    def _select_operation(
        self,
        available_ops: List[Tuple[int, int]],
        instance: JSSPInstance,
        job_available_time: List[int]
    ) -> Tuple[int, int]:
        """Select operation based on dispatching rule."""
        raise NotImplementedError


class SPTDispatcher(DispatchingRuleSolver):
    """Shortest Processing Time dispatching rule."""
    
    def __init__(self):
        super().__init__("SPT")
    
    def _select_operation(self, available_ops, instance, job_available_time):
        """Select operation with shortest processing time."""
        return min(
            available_ops,
            key=lambda op: instance.jobs[op[0]][op[1]][1]  # proc_time
        )


class LPTDispatcher(DispatchingRuleSolver):
    """Longest Processing Time dispatching rule."""
    
    def __init__(self):
        super().__init__("LPT")
    
    def _select_operation(self, available_ops, instance, job_available_time):
        """Select operation with longest processing time."""
        return max(
            available_ops,
            key=lambda op: instance.jobs[op[0]][op[1]][1]  # proc_time
        )
