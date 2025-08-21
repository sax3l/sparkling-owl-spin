"""
Anti-Bot Diagnostics Module - Website protection analysis.

Provides comprehensive analysis of website anti-bot measures including:
- Bot detection signal analysis
- Protection mechanism identification
- Risk assessment and scoring
- Mitigation strategy recommendations

Main Components:
- DiagnoseURL: Comprehensive URL protection analysis
- BotDetectionSignal: Individual detection signal representation
- DiagnosticResult: Complete analysis results
"""

from .diagnose_url import URLDiagnostic, DiagnosticResult, BotDetectionSignal

__all__ = [
    "URLDiagnostic",
    "DiagnosticResult",
    "BotDetectionSignal"
]