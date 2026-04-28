"""LLM-based scheduling approach."""
import json
import os
from typing import Dict, Optional
from src.data import JSSPInstance, JSSPSchedule
from src.baselines import LPTDispatcher


class LLMScheduler:
    """LLM-augmented JSSP scheduler."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize LLM scheduler.
        
        Args:
            api_key: API key for the LLM service.
            model: Model identifier (e.g., "gpt-4", "claude-3").
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.fallback_solver = LPTDispatcher()
    
    def solve(self, instance: JSSPInstance, use_fallback: bool = True) -> JSSPSchedule:
        """
        Solve using LLM with fallback to heuristic.
        
        Args:
            instance: The JSSP instance.
            use_fallback: If True, use fallback solver if LLM fails.
        
        Returns:
            JSSPSchedule solution.
        """
        # For now, return fallback solution
        # In production, this would call an LLM API
        
        if use_fallback:
            schedule = self.fallback_solver.solve(instance)
            schedule.metadata = {
                "method": "LLM (fallback to LPT)",
                "reason": "LLM API not configured"
            }
            return schedule
        
        raise RuntimeError("LLM scheduler not configured. Set OPENAI_API_KEY environment variable.")
    
    def _format_instance_for_llm(self, instance: JSSPInstance) -> str:
        """Format JSSP instance as JSON for LLM prompt."""
        jobs_data = []
        for job_id, job in enumerate(instance.jobs):
            job_ops = []
            for op_idx, (machine_id, proc_time) in enumerate(job):
                job_ops.append({
                    "operation": op_idx,
                    "machine": machine_id,
                    "processing_time": proc_time
                })
            jobs_data.append({
                "job_id": job_id,
                "operations": job_ops
            })
        
        return json.dumps({
            "num_jobs": instance.num_jobs,
            "num_machines": instance.num_machines,
            "jobs": jobs_data
        }, indent=2)
    
    def _parse_llm_schedule(
        self,
        llm_response: str,
        instance: JSSPInstance
    ) -> Optional[JSSPSchedule]:
        """Parse LLM response into schedule."""
        # Try to extract JSON from response
        try:
            # Find JSON in response
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = llm_response[start_idx:end_idx]
                schedule_data = json.loads(json_str)
                
                # Convert to internal format
                start_times = {}
                end_times = {}
                machine_schedule = {m: [] for m in range(instance.num_machines)}
                
                for job_id, ops in enumerate(schedule_data.get("schedule", {}).items()):
                    for op_idx, timing in enumerate(ops[1]):
                        start_times[(job_id, op_idx)] = timing["start"]
                        end_times[(job_id, op_idx)] = timing["end"]
                        
                        machine_id = instance.jobs[job_id][op_idx][0]
                        machine_schedule[machine_id].append(
                            (job_id, op_idx, timing["start"], timing["end"])
                        )
                
                makespan = max(
                    end_times.get((job_id, len(instance.jobs[job_id]) - 1), 0)
                    for job_id in range(instance.num_jobs)
                )
                
                return JSSPSchedule(
                    start_times=start_times,
                    end_times=end_times,
                    machine_schedule=machine_schedule,
                    makespan=makespan,
                    feasible=True
                )
        except (json.JSONDecodeError, KeyError, IndexError):
            pass
        
        return None
