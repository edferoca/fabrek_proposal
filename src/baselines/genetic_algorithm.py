"""Genetic Algorithm solver for JSSP."""
import random
from typing import List, Tuple
import numpy as np
from src.data import JSSPInstance, JSSPSchedule


class GeneticAlgorithmSolver:
    """Genetic Algorithm solver for JSSP."""
    
    def __init__(
        self,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        seed: int = None
    ):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def solve(self, instance: JSSPInstance) -> JSSPSchedule:
        """Solve using genetic algorithm."""
        # Generate initial population
        population = [
            self._generate_random_sequence(instance)
            for _ in range(self.population_size)
        ]
        
        best_schedule = None
        best_makespan = float('inf')
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            schedules = []
            
            for sequence in population:
                schedule = self._decode_sequence(sequence, instance)
                schedules.append(schedule)
                
                if schedule.feasible:
                    fitness = 1.0 / schedule.makespan
                    fitness_scores.append(fitness)
                    
                    if schedule.makespan < best_makespan:
                        best_makespan = schedule.makespan
                        best_schedule = schedule
                else:
                    fitness_scores.append(0.001)
            
            # Selection (tournament)
            selected = self._tournament_selection(population, fitness_scores, 2)
            
            # Crossover and mutation
            new_population = []
            while len(new_population) < self.population_size:
                if random.random() < self.crossover_rate:
                    parent1, parent2 = random.sample(selected, 2)
                    child = self._crossover(parent1, parent2)
                else:
                    child = random.choice(selected).copy()
                
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population
        
        return best_schedule if best_schedule else schedules[0]
    
    def _generate_random_sequence(self, instance: JSSPInstance) -> List[Tuple[int, int]]:
        """Generate a random operation sequence."""
        sequence = []
        for job_id in range(instance.num_jobs):
            for op_idx in range(len(instance.jobs[job_id])):
                sequence.append((job_id, op_idx))
        
        random.shuffle(sequence)
        return sequence
    
    def _decode_sequence(
        self,
        sequence: List[Tuple[int, int]],
        instance: JSSPInstance
    ) -> JSSPSchedule:
        """Decode operation sequence into schedule."""
        job_available_time = [0] * instance.num_jobs
        machine_available_time = [0] * instance.num_machines
        
        start_times = {}
        end_times = {}
        machine_schedule = {m: [] for m in range(instance.num_machines)}
        
        for job_id, op_idx in sequence:
            machine_id, proc_time = instance.jobs[job_id][op_idx]
            
            start_time = max(job_available_time[job_id], machine_available_time[machine_id])
            end_time = start_time + proc_time
            
            start_times[(job_id, op_idx)] = start_time
            end_times[(job_id, op_idx)] = end_time
            job_available_time[job_id] = end_time
            machine_available_time[machine_id] = end_time
            machine_schedule[machine_id].append((job_id, op_idx, start_time, end_time))
        
        makespan = max(machine_available_time)
        
        return JSSPSchedule(
            start_times=start_times,
            end_times=end_times,
            machine_schedule=machine_schedule,
            makespan=makespan,
            feasible=True
        )
    
    def _tournament_selection(
        self,
        population: List,
        fitness_scores: List[float],
        tournament_size: int
    ) -> List:
        """Select individuals using tournament selection."""
        selected = []
        for _ in range(len(population)):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            winner = max(
                tournament_indices,
                key=lambda i: fitness_scores[i]
            )
            selected.append(population[winner].copy())
        
        return selected
    
    def _crossover(self, parent1: List, parent2: List) -> List:
        """Perform order crossover (OX)."""
        size = len(parent1)
        point1 = random.randint(0, size - 1)
        point2 = random.randint(point1, size)
        
        child = parent1[point1:point2]
        
        for item in parent2:
            if item not in child:
                child.append(item)
        
        return child[:size]
    
    def _mutate(self, sequence: List) -> List:
        """Perform swap mutation."""
        sequence = sequence.copy()
        i, j = random.sample(range(len(sequence)), 2)
        sequence[i], sequence[j] = sequence[j], sequence[i]
        return sequence
