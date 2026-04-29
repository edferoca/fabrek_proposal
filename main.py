"""
Main entry point for JSSP solver.
Demonstrates all approaches on a sample instance.
"""

import time
from dotenv import load_dotenv
from src.data import generate_random_jssp, JSSPInstance
from src.baselines import SPTDispatcher, LPTDispatcher, GeneticAlgorithmSolver, CPSATSolver
from src.ml_approaches import LLMScheduler, MLScheduler
from src.utils import evaluate_schedule, visualize_gantt_chart, plot_comparison


def main():
    """Run all solvers and compare results."""
    
    # ✅ CARGAR VARIABLES DEL .env
    load_dotenv()
    
    print("=" * 80)
    print("JSSP Solver - Comprehensive Benchmark")
    print("=" * 80)
    
    # Generate or load instance
    print("\n[1] Generating JSSP instance...")
    instance = generate_random_jssp(
        num_jobs=6,
        num_machines=6,
        min_proc_time=5,
        max_proc_time=15,
        seed=42
    )
    print(f"    Instance: {instance}")
    print(f"    Total processing time (lower bound): {instance.get_total_processing_time()}")
    
    schedules = {}
    computation_times = {}
    
    # Baseline 1: SPT
    print("\n[2] Running SPT (Shortest Processing Time)...")
    spt_solver = SPTDispatcher()
    start_t = time.time()
    schedules["SPT"] = spt_solver.solve(instance)
    computation_times["SPT"] = time.time() - start_t
    print(f"    Makespan: {schedules['SPT'].makespan}, Time: {computation_times['SPT']:.4f}s")
    
    # Baseline 2: LPT
    print("\n[3] Running LPT (Longest Processing Time)...")
    lpt_solver = LPTDispatcher()
    start_t = time.time()
    schedules["LPT"] = lpt_solver.solve(instance)
    computation_times["LPT"] = time.time() - start_t
    print(f"    Makespan: {schedules['LPT'].makespan}, Time: {computation_times['LPT']:.4f}s")
    
    # Baseline 3: Genetic Algorithm
    print("\n[4] Running Genetic Algorithm...")
    ga_solver = GeneticAlgorithmSolver(population_size=30, generations=50, seed=42)
    start_t = time.time()
    schedules["GA"] = ga_solver.solve(instance)
    computation_times["GA"] = time.time() - start_t
    print(f"    Makespan: {schedules['GA'].makespan}, Time: {computation_times['GA']:.4f}s")
    
    # Baseline 4: OR-Tools CP-SAT
    print("\n[5] Running OR-Tools CP-SAT Solver...")
    cpsat_solver = CPSATSolver(time_limit_seconds=10)
    start_t = time.time()
    schedules["CP-SAT"] = cpsat_solver.solve(instance)
    computation_times["CP-SAT"] = time.time() - start_t
    print(f"    Makespan: {schedules['CP-SAT'].makespan}, Time: {computation_times['CP-SAT']:.4f}s")
    
    # ML/LLM Approach: LLM Scheduler
    print("\n[6] Running LLM-augmented Scheduler (Gemini)...")
    llm_solver = LLMScheduler()
    start_t = time.time()
    schedules["LLM (Gemini)"] = llm_solver.solve(instance)
    computation_times["LLM (Gemini)"] = time.time() - start_t
    print(f"    Makespan: {schedules['LLM (Gemini)'].makespan}, Time: {computation_times['LLM (Gemini)']:.4f}s")
    
    # ML Approach: ML Scheduler (scikit-learn)
    print("\n[7] Running ML Scheduler (scikit-learn features)...")
    ml_solver = MLScheduler(strategy="ensemble")
    start_t = time.time()
    schedules["ML (Feature-based)"] = ml_solver.solve(instance)
    computation_times["ML (Feature-based)"] = time.time() - start_t
    print(f"    Makespan: {schedules['ML (Feature-based)'].makespan}, Time: {computation_times['ML (Feature-based)']:.4f}s")
    
    # Print comparison
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Method':<20} {'Makespan':<12} {'Time (s)':<12} {'Feasible':<10}")
    print("-" * 55)
    
    best_makespan = float('inf')
    for method, schedule in schedules.items():
        comp_time = computation_times[method]
        makespan = schedule.makespan
        feasible = "Yes" if schedule.feasible else "No"
        
        print(f"{method:<20} {makespan:<12} {comp_time:<12.4f} {feasible:<10}")
        
        if schedule.feasible:
            best_makespan = min(best_makespan, makespan)
    
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    feasible_methods = {k: v for k, v in schedules.items() if v.feasible}
    if feasible_methods:
        best_method = min(feasible_methods, key=lambda k: feasible_methods[k].makespan)
        best_schedule = feasible_methods[best_method]
        
        print(f"\nBest solution: {best_method} (makespan: {best_schedule.makespan})")
        print(f"Gap from lower bound: {(best_schedule.makespan - instance.get_total_processing_time()) / instance.get_total_processing_time() * 100:.2f}%")
        
        # Visualize best schedule
        print(f"\nGenerating Gantt chart for {best_method}...")
        visualize_gantt_chart(
            instance,
            best_schedule,
            title=f"Best Schedule ({best_method}): Makespan = {best_schedule.makespan}",
            output_file="results/best_schedule.png"
        )

        # Comparison chart across all methods
        print(f"\nGenerating comparison chart...")
        from src.utils import evaluate_schedule
        from src.utils.evaluation import calculate_metrics
        metrics = calculate_metrics(instance, schedules, computation_times)
        plot_comparison(
            metrics,
            metric="makespan",
            output_file="results/comparison_makespan.png"
        )
        plot_comparison(
            metrics,
            metric="computation_time",
            output_file="results/comparison_time.png"
        )
        print("Comparison charts saved to results/")
    
    print("\n" + "=" * 80)
    print("✓ Benchmark complete! Check 'results/' directory for outputs.")
    print("=" * 80)


if __name__ == "__main__":
    main()
