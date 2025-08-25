"""
Sparkling-Owl-Spin Architecture Layers
The Four-Layer Sparkling-Owl-Spin Pyramid Implementation

Layer 1: Orchestration & AI Layer - The Brain. Makes decisions.
Layer 2: Execution & Acquisition Layer - The Body. Executes tasks.
Layer 3: Resistance & Bypass Layer - Shield and lubricant. Overcomes obstacles.
Layer 4: Processing & Analysis Layer - The senses. Extracts and analyzes data.
"""

from .bypass_layer import BypassLayer
from .execution_layer import ExecutionLayer
from .analysis_layer import AnalysisLayer
from .orchestration_layer import OrchestrationLayer

__all__ = [
    "BypassLayer",
    "ExecutionLayer", 
    "AnalysisLayer",
    "OrchestrationLayer"
]

__version__ = "4.0.0"
