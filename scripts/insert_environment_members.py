#!/usr/bin/env python3
"""
Script to insert membership lists into environment YAML files.
"""

import yaml
from pathlib import Path
import re

def insert_membership_into_yaml(yaml_file: Path, members_file: Path):
    """Insert membership list from members_file into yaml_file."""
    # Read the YAML file
    with open(yaml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Read the membership list
    with open(members_file, 'r', encoding='utf-8') as f:
        members_content = f.read().strip()
    
    # Find where to insert (after other_names, before notes)
    # Look for the pattern: other_names section ends, then notes or membership_count
    pattern = r'(other_names:.*?\n(?:- id: [^\n]+\n  name: [^\n]+\n)+)(notes:|membership_count:)'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Insert members after other_names
        new_content = content[:match.end(1)] + '\n' + members_content + '\n' + content[match.end(1):]
    else:
        # Fallback: insert before notes or membership_count
        pattern2 = r'(\n)(notes:|membership_count:)'
        match2 = re.search(pattern2, content)
        if match2:
            new_content = content[:match2.start(1)+1] + members_content + '\n' + content[match2.start(1)+1:]
        else:
            print(f"Warning: Could not find insertion point in {yaml_file}")
            return False
    
    # Write back
    with open(yaml_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent / "data" / "intblocks" / "environment"
    
    # Map of YAML files to their membership files
    mappings = {
        "UNFCCC.yaml": "UNFCCC_members.txt",
        "VIENNACONVENTION.yaml": "VIENNACONVENTION_members.txt",
        "MONTREALPROTOCOL.yaml": "MONTREALPROTOCOL_members.txt",
        "UNCCD.yaml": "UNCCD_members.txt",
        "PARISAGREEMENT.yaml": "PARISAGREEMENT_members.txt",
        "KYOTOPROTOCOL.yaml": "KYOTOPROTOCOL_members.txt",
        "CBD.yaml": "CBD_members.txt",
        "CITES.yaml": "CITES_members.txt",
    }
    
    for yaml_file, members_file in mappings.items():
        yaml_path = base_dir / yaml_file
        members_path = base_dir / members_file
        
        if yaml_path.exists() and members_path.exists():
            print(f"Processing {yaml_file}...")
            if insert_membership_into_yaml(yaml_path, members_path):
                print(f"  ✓ Successfully inserted members from {members_file}")
            else:
                print(f"  ✗ Failed to insert members")
        else:
            print(f"  ✗ Files not found: {yaml_path.exists()}, {members_path.exists()}")
