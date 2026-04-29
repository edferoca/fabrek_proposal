"""Visualization utilities for JSSP solutions."""
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — safe in all environments
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, Tuple, List
import numpy as np
from src.data import JSSPInstance, JSSPSchedule


def visualize_gantt_chart(
    instance: JSSPInstance,
    schedule: JSSPSchedule,
    title: str = None,
    output_file: str = None,
    figsize: Tuple[int, int] = (14, 8)
) -> None:
    """
    Visualize a JSSP schedule as a Gantt chart.
    
    Args:
        instance: The JSSP instance.
        schedule: The schedule to visualize.
        title: Title for the chart.
        output_file: Path to save the figure (if provided).
        figsize: Figure size (width, height).
    """
    if not schedule.feasible:
        print("Warning: Schedule is not feasible")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Colors for different jobs
    colors = plt.cm.Set3(np.linspace(0, 1, instance.num_jobs))
    
    # Plot operations on machines
    for machine_id in range(instance.num_machines):
        machine_ops = schedule.machine_schedule.get(machine_id, [])
        
        for job_id, op_idx, start_time, end_time in machine_ops:
            duration = end_time - start_time
            ax.barh(
                machine_id,
                duration,
                left=start_time,
                height=0.8,
                color=colors[job_id],
                edgecolor='black',
                linewidth=1.5
            )
            
            # Add label
            ax.text(
                start_time + duration / 2,
                machine_id,
                f"J{job_id}-O{op_idx}",
                ha='center',
                va='center',
                fontsize=9,
                fontweight='bold'
            )
    
    # Configure axes
    ax.set_ylim(-0.5, instance.num_machines - 0.5)
    ax.set_xlim(0, schedule.makespan * 1.05)
    ax.set_xlabel("Time", fontsize=12, fontweight='bold')
    ax.set_ylabel("Machine", fontsize=12, fontweight='bold')
    ax.set_yticks(range(instance.num_machines))
    ax.set_yticklabels([f"M{i}" for i in range(instance.num_machines)])
    ax.grid(True, axis='x', alpha=0.3)
    
    # Title
    if title is None:
        title = f"JSSP Schedule - Makespan: {schedule.makespan}"
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Legend for jobs
    job_patches = [
        mpatches.Patch(color=colors[i], label=f"Job {i}")
        for i in range(instance.num_jobs)
    ]
    ax.legend(handles=job_patches, loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Gantt chart saved to {output_file}")
    else:
        plt.show()

    plt.close(fig)


def plot_comparison(
    results: Dict,
    metric: str = "makespan",
    output_file: str = None
) -> None:
    """
    Plot comparison of different methods.
    
    Args:
        results: Dictionary of method_name -> metrics.
        metric: Which metric to plot.
        output_file: Path to save the figure.
    """
    methods = [k for k in results.keys() if k not in ["best_makespan"]]
    values = [results[m][metric] for m in methods if metric in results[m]]
    
    if not values:
        print(f"No data available for metric: {metric}")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(methods, values, color='steelblue', edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel(metric.replace("_", " ").title(), fontsize=12, fontweight='bold')
    ax.set_xlabel("Method", fontsize=12, fontweight='bold')
    ax.set_title(f"Comparison: {metric.replace('_', ' ').title()}", fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{height:.1f}',
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Comparison chart saved to {output_file}")
    else:
        plt.show()

    plt.close(fig)
