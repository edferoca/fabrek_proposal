"""Data module for JSSP instances."""
from .jssp_instance import JSSPInstance, JSSPSchedule
from .generators import generate_random_jssp

__all__ = ["JSSPInstance", "JSSPSchedule", "generate_random_jssp"]
