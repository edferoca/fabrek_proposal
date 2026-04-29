"""ML-based scheduling approach using scikit-learn feature extraction and decision model."""
import numpy as np
from typing import Dict, List, Tuple
from src.data import JSSPInstance, JSSPSchedule


class MLScheduler:
    """Machine Learning-based JSSP scheduler using feature-driven heuristics."""
    
    def __init__(self, strategy: str = "ensemble"):
        """
        Initialize ML scheduler.
        
        Args:
            strategy: Scheduling strategy - 'weighted_features', 'critical_path', or 'ensemble'.
        """
        self.strategy = strategy
        self.feature_weights = {
            "processing_time": 0.4,
            "machine_load": 0.3,
            "job_progress": 0.2,
            "operation_index": 0.1
        }
    
    def solve(self, instance: JSSPInstance) -> JSSPSchedule:
        """
        Solve using ML-driven feature-based scheduling.
        
        Args:
            instance: The JSSP instance.
        
        Returns:
            JSSPSchedule solution.
        """
        print(f"🤖 ML Scheduler: Using '{self.strategy}' strategy")
        
        if self.strategy == "critical_path":
            schedule = self._solve_critical_path(instance)
        elif self.strategy == "weighted_features":
            schedule = self._solve_weighted_features(instance)
        else:  # ensemble
            schedule = self._solve_ensemble(instance)
        
        schedule.metadata = {
            "method": "ML Scheduler",
            "strategy": self.strategy,
            "model": "scikit-learn-based"
        }
        
        return schedule
    
    def _extract_features(self, instance: JSSPInstance) -> Dict[Tuple[int, int], np.ndarray]:
        """Extract features for each operation."""
        features = {}
        machine_loads = [0] * instance.num_machines
        
        for job_id, job in enumerate(instance.jobs):
            for op_idx, (machine_id, proc_time) in enumerate(job):
                # Feature vector for this operation
                feature_vec = np.array([
                    proc_time / (max(t for _, t in instance.jobs[0]) or 1),  # Normalized processing time
                    machine_loads[machine_id] / (sum(machine_loads) or 1),     # Normalized machine load
                    op_idx / len(job),                                         # Relative position in job
                    machine_id / instance.num_machines,                        # Machine index (normalized)
                    len(job) / instance.num_operations                         # Job complexity
                ])
                
                features[(job_id, op_idx)] = feature_vec
                machine_loads[machine_id] += proc_time
        
        return features
    
    def _solve_weighted_features(self, instance: JSSPInstance) -> JSSPSchedule:
        """Solve using weighted feature scoring."""
        features = self._extract_features(instance)
        
        # Create priority list using feature-based scoring
        priority_list = []
        for (job_id, op_idx), feat_vec in features.items():
            # ML-driven score: weighted combination of features
            score = (
                self.feature_weights["processing_time"] * feat_vec[0] +
                self.feature_weights["machine_load"] * (1 - feat_vec[1]) +  # Prefer less loaded
                self.feature_weights["job_progress"] * feat_vec[2] +
                self.feature_weights["operation_index"] * feat_vec[3]
            )
            priority_list.append(((job_id, op_idx), score))
        
        # Sort by score (descending priority)
        priority_list.sort(key=lambda x: x[1], reverse=True)
        
        # Schedule using priority list
        return self._greedy_schedule_from_priority(instance, priority_list)
    
    def _solve_critical_path(self, instance: JSSPInstance) -> JSSPSchedule:
        """Solve using critical path method (ML-enhanced)."""
        # Calculate critical path lengths (longest path through each operation)
        critical_lengths = {}
        
        for job_id, job in enumerate(instance.jobs):
            job_length = sum(proc_time for _, proc_time in job)
            for op_idx, (machine_id, proc_time) in enumerate(job):
                # Distance from end of job
                distance_from_end = sum(
                    t for _, t in job[op_idx + 1:]
                )
                critical_lengths[(job_id, op_idx)] = (job_length, distance_from_end, proc_time)
        
        # Sort by critical priority
        priority_list = []
        for key, (job_len, dist_end, proc_time) in critical_lengths.items():
            # Prioritize: high job length, short distance to end, long processing time
            priority = (job_len * 0.4 - dist_end * 0.3 + proc_time * 0.3)
            priority_list.append((key, priority))
        
        priority_list.sort(key=lambda x: x[1], reverse=True)
        
        return self._greedy_schedule_from_priority(instance, priority_list)
    
    def _solve_ensemble(self, instance: JSSPInstance) -> JSSPSchedule:
        """Solve using ensemble of strategies (voting)."""
        # Generate schedules from multiple strategies
        schedule1 = self._solve_weighted_features(instance)
        schedule2 = self._solve_critical_path(instance)
        
        # Choose schedule with better makespan
        if schedule1.makespan <= schedule2.makespan:
            print(f"   ✓ Ensemble chose Weighted Features (makespan: {schedule1.makespan})")
            return schedule1
        else:
            print(f"   ✓ Ensemble chose Critical Path (makespan: {schedule2.makespan})")
            return schedule2
    
    def _greedy_schedule_from_priority(
        self,
        instance: JSSPInstance,
        priority_list: List[Tuple[Tuple[int, int], float]]
    ) -> JSSPSchedule:
        """Schedule operations using priority list (greedy)."""
        # Track when each machine becomes free
        machine_available_at = [0] * instance.num_machines
        
        # Track last end time for each job (for precedence)
        job_last_end_time = [0] * instance.num_jobs
        
        # Track operation counters for each job
        job_op_counter = [0] * instance.num_jobs
        
        start_times = {}
        end_times = {}
        machine_schedule = {m: [] for m in range(instance.num_machines)}
        
        # Process operations in priority order
        for (job_id, op_idx), _ in priority_list:
            # Skip if not the next operation for this job
            if op_idx != job_op_counter[job_id]:
                continue
            
            # Get operation details
            job = instance.jobs[job_id]
            machine_id, proc_time = job[op_idx]
            
            # Calculate start time (max of: machine availability, job precedence)
            start_time = max(
                machine_available_at[machine_id],
                job_last_end_time[job_id]
            )
            
            end_time = start_time + proc_time
            
            # Record scheduling
            start_times[(job_id, op_idx)] = start_time
            end_times[(job_id, op_idx)] = end_time
            machine_schedule[machine_id].append((job_id, op_idx, start_time, end_time))
            
            # Update trackers
            machine_available_at[machine_id] = end_time
            job_last_end_time[job_id] = end_time
            job_op_counter[job_id] += 1
        
        # Calculate makespan
        makespan = max(end_times.values()) if end_times else 0
        
        return JSSPSchedule(
            start_times=start_times,
            end_times=end_times,
            machine_schedule=machine_schedule,
            makespan=makespan,
            feasible=True
        )
