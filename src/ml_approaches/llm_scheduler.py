"""LLM-based scheduling approach using Google Gemini."""
import json
import os
import re
from typing import Dict, Optional
from src.data import JSSPInstance, JSSPSchedule
from src.baselines import LPTDispatcher

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMScheduler:
    """LLM-augmented JSSP scheduler using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-flash-latest"):
        """
        Initialize LLM scheduler with Gemini.
        
        Args:
            api_key: Google Gemini API key (or set GEMINI_API_KEY env var).
            model: Model identifier (e.g., "gemini-pro", "gemini-1.5-pro").
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL")
        self.fallback_solver = LPTDispatcher()
        self.gemini_available = GEMINI_AVAILABLE and self.api_key is not None
        
        if self.gemini_available:
            genai.configure(api_key=self.api_key)
            self.llm_model = genai.GenerativeModel(model)
    
    def solve(self, instance: JSSPInstance, use_fallback: bool = True) -> JSSPSchedule:
        """
        Solve using Gemini LLM with fallback to heuristic.
        
        Args:
            instance: The JSSP instance.
            use_fallback: If True, use fallback solver if LLM fails.
        
        Returns:
            JSSPSchedule solution.
        """
        if not self.gemini_available:
            msg = "❌ Gemini LLM UNAVAILABLE"
            reason = "Gemini API not configured. Set GEMINI_API_KEY environment variable."
            print(f"\n{msg}")
            print(f"📋 Reason: {reason}")
            
            if use_fallback:
                print("🔄 Falling back to LPT (Longest Processing Time) dispatcher\n")
                schedule = self.fallback_solver.solve(instance)
                schedule.metadata = {
                    "method": "LLM (fallback to LPT)",
                    "reason": reason,
                    "gemini_call_made": False
                }
                return schedule
            else:
                raise RuntimeError(
                    f"{msg}: {reason}"
                )
        
        try:
            # Format instance for LLM
            formatted_instance = self._format_instance_for_llm(instance)
            
            # Create prompt
            prompt = self._create_prompt(formatted_instance, instance)
            
            # Call Gemini API
            response = self.llm_model.generate_content(prompt)
            
            # Parse response
            schedule = self._parse_llm_schedule(response.text, instance)
            
            if schedule is None:
                raise ValueError("Failed to parse LLM response")
            
            schedule.metadata = {
                "method": "Gemini LLM",
                "model": self.model,
                "success": True
            }
            
            return schedule
            
        except Exception as e:
            msg = "❌ Gemini LLM API CALL FAILED"
            print(f"\n{msg}")
            print(f"📋 Error: {type(e).__name__}: {str(e)}")
            print(f"⏱️  Gemini was attempted but could not complete\n")
            
            if use_fallback:
                print("🔄 Falling back to LPT (Longest Processing Time) dispatcher\n")
                schedule = self.fallback_solver.solve(instance)
                schedule.metadata = {
                    "method": "LLM (fallback to LPT)",
                    "reason": f"Gemini API error: {str(e)}",
                    "gemini_call_made": True,
                    "gemini_failed": True,
                    "error_type": type(e).__name__
                }
                return schedule
            else:
                raise
    
    def _create_prompt(self, formatted_instance: str, instance: JSSPInstance) -> str:
        """Create structured prompt for Gemini."""
        return f"""You are an expert operations researcher specializing in the Job Shop Scheduling Problem (JSSP).

Given the following JSSP instance, generate an optimal or near-optimal schedule that:
1. Minimizes makespan (total completion time)
2. Respects all precedence constraints (jobs must follow operation order)
3. Respects machine capacity (each machine processes one job at a time)

JSSP Instance:
{formatted_instance}

Please provide your response in the following JSON format:
{{
  "schedule": [
    {{
      "job_id": 0,
      "operations": [
        {{"operation_idx": 0, "machine_id": 2, "start_time": 0, "duration": 8}},
        {{"operation_idx": 1, "machine_id": 1, "start_time": 8, "duration": 5}}
      ]
    }}
  ],
  "makespan": 13,
  "reasoning": "Brief explanation of the scheduling strategy"
}}

Guidelines:
- Each operation must start after the previous operation of the same job finishes
- Each operation's duration is fixed as specified in the instance
- Operations on the same machine cannot overlap
- Calculate makespan as the maximum end time across all operations
- Provide your best feasible schedule

Please respond with ONLY the JSON, no additional text."""
    
    def _format_instance_for_llm(self, instance: JSSPInstance) -> str:
        """Format JSSP instance as JSON for LLM prompt."""
        jobs_data = []
        for job_id, job in enumerate(instance.jobs):
            job_ops = []
            for op_idx, (machine_id, proc_time) in enumerate(job):
                job_ops.append({
                    "operation_index": op_idx,
                    "machine_id": machine_id,
                    "processing_time": proc_time
                })
            jobs_data.append({
                "job_id": job_id,
                "operations": job_ops
            })
        
        return json.dumps({
            "problem": {
                "num_jobs": instance.num_jobs,
                "num_machines": instance.num_machines,
                "total_operations": instance.num_operations
            },
            "jobs": jobs_data
        }, indent=2)
    
    def _parse_llm_schedule(
        self,
        llm_response: str,
        instance: JSSPInstance
    ) -> Optional[JSSPSchedule]:
        """Parse Gemini response into schedule."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if not json_match:
                print("❌ No JSON found in response")
                return None
            
            json_str = json_match.group(0)
            response_data = json.loads(json_str)
            
            # Extract schedule
            schedule_data = response_data.get("schedule", [])
            
            # Convert to internal format
            start_times = {}
            end_times = {}
            machine_schedule = {m: [] for m in range(instance.num_machines)}
            
            max_end_time = 0
            
            for job_info in schedule_data:
                job_id = job_info.get("job_id")
                operations = job_info.get("operations", [])
                
                for op_data in operations:
                    op_idx = op_data.get("operation_idx")
                    machine_id = op_data.get("machine_id")
                    start_time = op_data.get("start_time")
                    duration = op_data.get("duration")
                    end_time = start_time + duration
                    
                    start_times[(job_id, op_idx)] = start_time
                    end_times[(job_id, op_idx)] = end_time
                    max_end_time = max(max_end_time, end_time)
                    
                    machine_schedule[machine_id].append(
                        (job_id, op_idx, start_time, end_time)
                    )
            
            # Use reported makespan if available, otherwise calculate
            makespan = response_data.get("makespan", max_end_time)
            
            return JSSPSchedule(
                start_times=start_times,
                end_times=end_times,
                machine_schedule=machine_schedule,
                makespan=makespan,
                feasible=True
            )
            
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            print(f"❌ Failed to parse LLM response: {e}")
            return None

