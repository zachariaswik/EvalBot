#!/usr/bin/env python3
"""Check Agent 7 rankings for duplicate startups across categories."""

import json
import sys
from pathlib import Path
from collections import defaultdict


def check_ranking_duplicates(ranking_file: Path) -> bool:
    """Check if any startups appear in multiple categories."""
    with open(ranking_file) as f:
        data = json.load(f)
    
    # Handle both direct and nested (raw_output) formats
    if "raw_output" in data:
        try:
            ranking = json.loads(data["raw_output"])
        except json.JSONDecodeError:
            print(f"⚠ Warning: Could not parse raw_output in {ranking_file}")
            return False
    else:
        ranking = data
    
    # Track startup appearances across categories
    startup_locations = defaultdict(list)
    
    categories = [
        "top_vc_candidates",
        "promising_need_focus",
        "promising_need_pivot",
        "good_small_businesses",
        "weak_ideas"
    ]
    
    for category in categories:
        items = ranking.get(category, [])
        for item in items:
            # Handle both string format and object format
            if isinstance(item, str):
                name = item
            elif isinstance(item, dict):
                name = item.get("name", "")
            else:
                continue
            
            if name:
                startup_locations[name].append(category)
    
    # Find duplicates
    duplicates = {name: cats for name, cats in startup_locations.items() if len(cats) > 1}
    
    if duplicates:
        print(f"\n❌ Found duplicates in {ranking_file.name}:")
        for name, categories in duplicates.items():
            print(f"   '{name}' appears in: {', '.join(categories)}")
        return True
    
    return False


def main():
    if len(sys.argv) > 1:
        ranking_file = Path(sys.argv[1])
        if not ranking_file.exists():
            print(f"Error: {ranking_file} not found")
            sys.exit(1)
        
        has_duplicates = check_ranking_duplicates(ranking_file)
        sys.exit(1 if has_duplicates else 0)
    
    # Check all ranking files
    output_dir = Path("output")
    ranking_files = list(output_dir.glob("*/ranking.json"))
    
    if not ranking_files:
        print("No ranking.json files found in output/")
        sys.exit(0)
    
    print(f"Checking {len(ranking_files)} ranking files...\n")
    
    files_with_duplicates = 0
    for ranking_file in ranking_files:
        if check_ranking_duplicates(ranking_file):
            files_with_duplicates += 1
    
    if files_with_duplicates == 0:
        print(f"\n✓ No duplicates found in {len(ranking_files)} ranking files")
    else:
        print(f"\n❌ Found duplicates in {files_with_duplicates}/{len(ranking_files)} ranking files")
        sys.exit(1)


if __name__ == "__main__":
    main()
