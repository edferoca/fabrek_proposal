"""OR-Tools CP-SAT solver for JSSP."""
from typing import Dict, Tuple, List
from ortools.sat.python import cp_model
from src.data import JSSPInstance, JSSPSchedule


class CPSATSolver:
    """Google OR-Tools CP-SAT solver for JSSP."""
    
    def __init__(self, time_limit_seconds: int = 60):
        self.time_limit_seconds = time_limit_seconds
    
    def solve(self, instance: JSSPInstance) -> JSSPSchedule:
        """Solve using CP-SAT solver."""
        model = cp_model.CpModel()
        
        # Decision variables
        horizon = instance.get_total_processing_time()
        task_vars = {}
        machine_vars = {}
        
        for job_id in range(instance.num_jobs):
            for op_idx, (machine_id, proc_time) in enumerate(instance.jobs[job_id]):
                start_var = model.NewIntVar(0, horizon, f'start_{job_id}_{op_idx}')
                end_var = model.NewIntVar(0, horizon, f'end_{job_id}_{op_idx}')
                interval_var = model.NewIntervalVar(
                    start_var, proc_time, end_var,
                    f'interval_{job_id}_{op_idx}'
                )
                
                task_vars[(job_id, op_idx)] = (start_var, end_var, interval_var, proc_time)
                
                if machine_id not in machine_vars:
                    machine_vars[machine_id] = []
                machine_vars[machine_id].append(interval_var)
        
        # Precedence constraints
        for job_id in range(instance.num_jobs):
            for op_idx in range(len(instance.jobs[job_id]) - 1):
                # task_vars stores (start_var, end_var, interval_var, proc_time)
                _, end_curr, _, _ = task_vars[(job_id, op_idx)]
                start_next, _, _, _ = task_vars[(job_id, op_idx + 1)]
                model.Add(start_next >= end_curr)
        
        # Machine constraints
        for machine_id, intervals in machine_vars.items():
            model.AddNoOverlap(intervals)
        
        # Objective: minimize makespan
        makespan_var = model.NewIntVar(0, horizon, 'makespan')
        model.AddMaxEquality(
            makespan_var,
            [task_vars[(job_id, len(instance.jobs[job_id]) - 1)][1]
             for job_id in range(instance.num_jobs)]
        )
        model.Minimize(makespan_var)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        status = solver.Solve(model)
        
        # Extract solution
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            start_times = {}
            end_times = {}
            machine_schedule = {m: [] for m in range(instance.num_machines)}
            
            for (job_id, op_idx), (start_var, end_var, _, _) in task_vars.items():
                start_time = solver.Value(start_var)
                end_time = solver.Value(end_var)
                
                start_times[(job_id, op_idx)] = start_time
                end_times[(job_id, op_idx)] = end_time
                
                machine_id = instance.jobs[job_id][op_idx][0]
                machine_schedule[machine_id].append((job_id, op_idx, start_time, end_time))
            
            makespan = solver.Value(makespan_var)
            
            return JSSPSchedule(
                start_times=start_times,
                end_times=end_times,
                machine_schedule=machine_schedule,
                makespan=makespan,
                feasible=True,
                metadata={"status": "CP-SAT"}
            )
        else:
            # Return infeasible schedule
            return JSSPSchedule(
                start_times={},
                end_times={},
                machine_schedule={},
                makespan=float('inf'),
                feasible=False,
                metadata={"status": "No solution found"}
            )
