#!/usr/bin/env python3
"""
TSVF Performance Metrics and Logging

Enhanced logging system to track TSVF weak values, variance reduction,
and retrocausal analysis metrics for empirical refinements.

Integrates with existing ladder_results.csv and creates TSVF-specific
performance visualizations.
"""

import csv
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import numpy as np

# Import TSVF components
from tsvf import TSVFState, TSVFOptimizer


# Constants
BITS_PER_BYTE = 8
MS_PER_SECOND = 1000
MAX_WEAK_VALUES_STORED = 100  # Maximum weak values to store in JSON


class TSVFMetricsLogger:
    """
    Logger for TSVF performance metrics and weak values.
    
    Tracks:
    - Weak value measurements
    - Variance reduction factors
    - Forward/backward evolution metrics
    - Candidate ranking performance
    - Time-symmetric distance measurements
    """
    
    def __init__(self, log_dir: str = "logs", csv_file: str = "tsvf_metrics.csv"):
        """
        Initialize TSVF metrics logger.
        
        Args:
            log_dir: Directory for log files
            csv_file: CSV filename for metrics
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.csv_path = self.log_dir / csv_file
        self.json_path = self.log_dir / "tsvf_metrics.jsonl"
        
        # Initialize CSV if needed
        if not self.csv_path.exists():
            self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file with headers."""
        headers = [
            "timestamp",
            "target_N",
            "dimension",
            "num_candidates",
            "variance_reduction",
            "avg_weak_value",
            "max_weak_value",
            "min_weak_value",
            "tsvf_enabled",
            "success",
            "time_ms",
            "notes"
        ]
        
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def log_factorization_attempt(self,
                                  target_N: int,
                                  dimension: int,
                                  num_candidates: int,
                                  variance_reduction: float,
                                  weak_values: List[float],
                                  tsvf_enabled: bool,
                                  success: bool,
                                  time_ms: float,
                                  notes: str = ""):
        """
        Log a factorization attempt with TSVF metrics.
        
        Args:
            target_N: Target semiprime
            dimension: Embedding dimension
            num_candidates: Number of candidates tested
            variance_reduction: TSVF variance reduction factor
            weak_values: List of weak value measurements
            tsvf_enabled: Whether TSVF was used
            success: Whether factorization succeeded
            time_ms: Time taken in milliseconds
            notes: Additional notes
        """
        timestamp = datetime.now().isoformat()
        
        # Compute statistics on weak values
        if weak_values:
            avg_weak = np.mean(weak_values)
            max_weak = np.max(weak_values)
            min_weak = np.min(weak_values)
        else:
            avg_weak = max_weak = min_weak = 0.0
        
        # Write to CSV
        row = [
            timestamp,
            target_N,
            dimension,
            num_candidates,
            f"{variance_reduction:.4f}",
            f"{avg_weak:.6f}",
            f"{max_weak:.6f}",
            f"{min_weak:.6f}",
            tsvf_enabled,
            success,
            f"{time_ms:.3f}",
            notes
        ]
        
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        # Write detailed JSON record
        record = {
            "timestamp": timestamp,
            "target_N": str(target_N),
            "dimension": dimension,
            "num_candidates": num_candidates,
            "variance_reduction": variance_reduction,
            "weak_values": {
                "avg": avg_weak,
                "max": max_weak,
                "min": min_weak,
                "values": weak_values[:MAX_WEAK_VALUES_STORED]  # Store first N values
            },
            "tsvf_enabled": tsvf_enabled,
            "success": success,
            "time_ms": time_ms,
            "notes": notes
        }
        
        with open(self.json_path, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def log_transec_performance(self,
                               operation: str,
                               tsvf_enabled: bool,
                               time_ms: float,
                               success: bool,
                               message_size: int,
                               notes: str = ""):
        """
        Log TRANSEC operation performance.
        
        Args:
            operation: 'encrypt' or 'decrypt'
            tsvf_enabled: Whether TSVF was used
            time_ms: Operation time in milliseconds
            success: Whether operation succeeded
            message_size: Message size in bytes
            notes: Additional notes
        """
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "type": "transec",
            "operation": operation,
            "tsvf_enabled": tsvf_enabled,
            "time_ms": time_ms,
            "success": success,
            "message_size": message_size,
            "throughput_mbps": ((message_size * BITS_PER_BYTE) / time_ms 
                              if time_ms > 0 else 0),
            "notes": notes
        }
        
        with open(self.json_path, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def log_weak_value_measurement(self,
                                   candidate: int,
                                   weak_value: complex,
                                   forward_state: TSVFState,
                                   backward_state: TSVFState,
                                   context: str = ""):
        """
        Log detailed weak value measurement.
        
        Args:
            candidate: Candidate being measured
            weak_value: Computed weak value
            forward_state: Forward TSVF state
            backward_state: Backward TSVF state
            context: Measurement context
        """
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "type": "weak_value",
            "candidate": candidate,
            "weak_value": {
                "real": weak_value.real,
                "imag": weak_value.imag,
                "magnitude": abs(weak_value),
                "phase": np.angle(weak_value)
            },
            "forward_state": {
                "amplitude": forward_state.amplitude,
                "phase": forward_state.phase,
                "coordinates": forward_state.coordinates.tolist()
            },
            "backward_state": {
                "amplitude": backward_state.amplitude,
                "phase": backward_state.phase,
                "coordinates": backward_state.coordinates.tolist()
            },
            "context": context
        }
        
        with open(self.json_path, 'a') as f:
            f.write(json.dumps(record) + '\n')


class TSVFPerformanceAnalyzer:
    """
    Analyzer for TSVF performance metrics.
    
    Generates summary statistics, comparisons, and insights from
    logged TSVF metrics.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize performance analyzer.
        
        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        self.csv_path = self.log_dir / "tsvf_metrics.csv"
        self.json_path = self.log_dir / "tsvf_metrics.jsonl"
    
    def load_metrics(self) -> List[Dict[str, Any]]:
        """
        Load all metrics from JSON log.
        
        Returns:
            List of metric records
        """
        if not self.json_path.exists():
            return []
        
        metrics = []
        with open(self.json_path, 'r') as f:
            for line in f:
                metrics.append(json.loads(line))
        
        return metrics
    
    def compare_tsvf_vs_standard(self) -> Dict[str, Any]:
        """
        Compare TSVF-enhanced vs standard performance.
        
        Returns:
            Comparison statistics
        """
        metrics = self.load_metrics()
        
        # Filter factorization attempts
        factorization_metrics = [
            m for m in metrics
            if 'num_candidates' in m and 'tsvf_enabled' in m
        ]
        
        if not factorization_metrics:
            return {"error": "No factorization metrics found"}
        
        # Split by TSVF enabled/disabled
        tsvf_metrics = [m for m in factorization_metrics if m['tsvf_enabled']]
        standard_metrics = [m for m in factorization_metrics if not m['tsvf_enabled']]
        
        def compute_stats(metrics_list):
            if not metrics_list:
                return None
            return {
                "count": len(metrics_list),
                "success_rate": sum(1 for m in metrics_list if m['success']) / len(metrics_list),
                "avg_time_ms": np.mean([m['time_ms'] for m in metrics_list]),
                "avg_variance_reduction": np.mean([m['variance_reduction'] for m in metrics_list]),
                "avg_weak_value": np.mean([m['weak_values']['avg'] for m in metrics_list]),
            }
        
        tsvf_stats = compute_stats(tsvf_metrics)
        standard_stats = compute_stats(standard_metrics)
        
        # Compute improvements safely
        improvement = {}
        if tsvf_stats and standard_stats:
            # Success rate improvement (handle zero denominator)
            if standard_stats['success_rate'] > 0:
                improvement['success_rate'] = tsvf_stats['success_rate'] / standard_stats['success_rate']
            else:
                improvement['success_rate'] = None
            
            # Variance reduction improvement (handle zero denominator)
            if standard_stats['avg_variance_reduction'] > 0:
                improvement['variance_reduction'] = (tsvf_stats['avg_variance_reduction'] / 
                                                   standard_stats['avg_variance_reduction'])
            else:
                improvement['variance_reduction'] = None
        
        return {
            "tsvf_enhanced": tsvf_stats,
            "standard": standard_stats,
            "improvement": improvement
        }
    
    def generate_summary_report(self, output_file: str = "tsvf_summary.md"):
        """
        Generate markdown summary report.
        
        Args:
            output_file: Output filename
        """
        metrics = self.load_metrics()
        comparison = self.compare_tsvf_vs_standard()
        
        report_path = self.log_dir / output_file
        
        with open(report_path, 'w') as f:
            f.write("# TSVF Performance Summary Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("## Overview\n\n")
            f.write(f"- Total metrics logged: {len(metrics)}\n")
            
            # Factorization metrics
            factorization_count = sum(1 for m in metrics if 'num_candidates' in m)
            f.write(f"- Factorization attempts: {factorization_count}\n")
            
            # TRANSEC metrics
            transec_count = sum(1 for m in metrics if m.get('type') == 'transec')
            f.write(f"- TRANSEC operations: {transec_count}\n")
            
            # Weak value measurements
            weak_value_count = sum(1 for m in metrics if m.get('type') == 'weak_value')
            f.write(f"- Weak value measurements: {weak_value_count}\n\n")
            
            if comparison.get('tsvf_enhanced') and comparison.get('standard'):
                f.write("## TSVF vs Standard Comparison\n\n")
                f.write("### TSVF-Enhanced\n")
                tsvf = comparison['tsvf_enhanced']
                f.write(f"- Attempts: {tsvf['count']}\n")
                f.write(f"- Success rate: {tsvf['success_rate']:.1%}\n")
                f.write(f"- Avg time: {tsvf['avg_time_ms']:.3f} ms\n")
                f.write(f"- Avg variance reduction: {tsvf['avg_variance_reduction']:.2f}x\n\n")
                
                f.write("### Standard\n")
                std = comparison['standard']
                f.write(f"- Attempts: {std['count']}\n")
                f.write(f"- Success rate: {std['success_rate']:.1%}\n")
                f.write(f"- Avg time: {std['avg_time_ms']:.3f} ms\n")
                f.write(f"- Avg variance reduction: {std['avg_variance_reduction']:.2f}x\n\n")
                
                f.write("### Improvement\n")
                if comparison['improvement']['success_rate']:
                    f.write(f"- Success rate improvement: {comparison['improvement']['success_rate']:.2f}x\n")
                if comparison['improvement']['variance_reduction']:
                    f.write(f"- Variance reduction improvement: {comparison['improvement']['variance_reduction']:.2f}x\n")
        
        print(f"Summary report written to {report_path}")


def demonstrate_tsvf_logging():
    """Demonstrate TSVF metrics logging."""
    print("=== TSVF Metrics Logging Demonstration ===\n")
    
    # Initialize logger
    logger = TSVFMetricsLogger()
    
    # Log some sample factorization attempts
    print("Logging factorization attempts...")
    
    # TSVF-enhanced attempt
    logger.log_factorization_attempt(
        target_N=899,
        dimension=5,
        num_candidates=100,
        variance_reduction=3.5,
        weak_values=[0.5, 0.6, 0.7, 0.8, 0.65],
        tsvf_enabled=True,
        success=True,
        time_ms=15.2,
        notes="TSVF-enhanced GVA on 899"
    )
    
    # Standard attempt
    logger.log_factorization_attempt(
        target_N=899,
        dimension=5,
        num_candidates=100,
        variance_reduction=1.0,
        weak_values=[0.3, 0.4, 0.35, 0.38, 0.32],
        tsvf_enabled=False,
        success=True,
        time_ms=12.8,
        notes="Standard GVA on 899"
    )
    
    # Log TRANSEC performance
    print("Logging TRANSEC operations...")
    logger.log_transec_performance(
        operation="encrypt",
        tsvf_enabled=True,
        time_ms=0.209,
        success=True,
        message_size=64,
        notes="TSVF-enhanced encryption"
    )
    
    logger.log_transec_performance(
        operation="decrypt",
        tsvf_enabled=True,
        time_ms=0.192,
        success=True,
        message_size=64,
        notes="TSVF-enhanced decryption"
    )
    
    print(f"\nMetrics logged to:")
    print(f"  - CSV: {logger.csv_path}")
    print(f"  - JSON: {logger.json_path}")
    print()
    
    # Generate summary report
    print("Generating summary report...")
    analyzer = TSVFPerformanceAnalyzer()
    analyzer.generate_summary_report()
    print()
    
    # Load and display comparison
    comparison = analyzer.compare_tsvf_vs_standard()
    if comparison.get('tsvf_enhanced'):
        print("Performance Comparison:")
        print(f"  TSVF Success Rate: {comparison['tsvf_enhanced']['success_rate']:.1%}")
        print(f"  Standard Success Rate: {comparison['standard']['success_rate']:.1%}")
        print(f"  TSVF Variance Reduction: {comparison['tsvf_enhanced']['avg_variance_reduction']:.2f}x")
        print(f"  Standard Variance Reduction: {comparison['standard']['avg_variance_reduction']:.2f}x")
    
    print("\nTSVF metrics logging demonstration complete!")


if __name__ == '__main__':
    demonstrate_tsvf_logging()
