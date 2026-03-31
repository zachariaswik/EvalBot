#!/usr/bin/env python3
"""Extract metrics from a generate run for analysis and comparison."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

def extract_metrics(batch_id: str, db_path: str = "evalbot.db") -> dict[str, Any]:
    """Extract metrics from database for a given batch_id."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get all Agent 2 outputs (venture analyst scores)
    cursor = conn.execute("""
        SELECT output_json 
        FROM agent_outputs 
        WHERE batch_id = ? AND agent_number = 2 AND is_current = 1
        ORDER BY created_at
    """, (batch_id,))
    
    scores = []
    dimensions = {
        'problem_severity': [],
        'market_size': [],
        'differentiation': [],
        'founder_insight': [],
        'moat_potential': [],
        'business_model': [],
        'venture_potential': []
    }
    
    for row in cursor:
        output = json.loads(row['output_json'])
        
        # Extract weighted score
        weighted_score = output.get('weighted_total_score', 0)
        scores.append(weighted_score)
        
        # Extract dimensional scores
        dim_scores = output.get('dimension_scores', {})
        for dim in dimensions:
            if dim in dim_scores:
                dimensions[dim].append(dim_scores[dim])
    
    conn.close()
    
    if not scores:
        return {"error": f"No data found for batch_id: {batch_id}"}
    
    # Calculate statistics
    import statistics
    
    metrics = {
        "batch_id": batch_id,
        "num_rounds": len(scores),
        "scores": {
            "weighted_total": scores,
            "average": statistics.mean(scores),
            "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
            "min": min(scores),
            "max": max(scores),
            "median": statistics.median(scores)
        },
        "dimensions": {}
    }
    
    # Calculate dimension statistics
    for dim, values in dimensions.items():
        if values:
            metrics["dimensions"][dim] = {
                "average": statistics.mean(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values)
            }
    
    return metrics


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_metrics.py <batch_id> [output_file.json]")
        print("\nExample: python extract_metrics.py generated_1")
        sys.exit(1)
    
    batch_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    metrics = extract_metrics(batch_id)
    
    if "error" in metrics:
        print(f"Error: {metrics['error']}")
        sys.exit(1)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Metrics for batch: {batch_id}")
    print(f"{'='*60}")
    print(f"Rounds completed: {metrics['num_rounds']}")
    print(f"\nWeighted Total Score (0-80):")
    print(f"  Average: {metrics['scores']['average']:.1f}")
    print(f"  Std Dev: {metrics['scores']['std_dev']:.1f}")
    print(f"  Range:   {metrics['scores']['min']:.0f} - {metrics['scores']['max']:.0f}")
    print(f"  Median:  {metrics['scores']['median']:.1f}")
    
    print(f"\nDimension Averages:")
    for dim, stats in metrics['dimensions'].items():
        print(f"  {dim.replace('_', ' ').title():20s}: {stats['average']:.1f} ± {stats['std_dev']:.1f}")
    
    print(f"\nAll Scores: {metrics['scores']['weighted_total']}")
    print(f"{'='*60}\n")
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Metrics saved to: {output_file}")


if __name__ == "__main__":
    main()
