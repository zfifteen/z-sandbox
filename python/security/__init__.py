"""
Security Module

This module contains security-related analysis tools including:
- Hyper-rotation protocol analysis
- Post-quantum cryptography resistance estimation
- Timing attack analysis

Separated from core factorization/validation to keep surfaces lean (MC-SCOPE-005).
"""

__all__ = ['HyperRotationMonteCarloAnalyzer']

from .hyper_rotation import HyperRotationMonteCarloAnalyzer
