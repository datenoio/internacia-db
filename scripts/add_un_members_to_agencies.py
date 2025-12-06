#!/usr/bin/env python3
"""
Script to add UN member country lists to UN agency files that are missing includes data.
"""

import yaml
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
UN_FILE = BASE_DIR / "data" / "intblocks" / "political" / "UN.yaml"
UNAGENCY_DIR = BASE_DIR / "data" / "intblocks" / "unagency"

# Files that should have UN member lists (all UN member states)
FILES_WITH_UN_MEMBERS = [
    "UNICEF.yaml",
    "UNHCR.yaml", 
    "UNAIDS.yaml",
    "UNOPS.yaml",
    "OHCHR.yaml",
    "UNDP.yaml",
    "UNEP.yaml",
    "WFP.yaml",
    "UNFPA.yaml",
    "UNHABITAT.yaml",
    "UNODC.yaml",
    "UNRWA.yaml",
    "UNWOMEN.yaml",
]

# Files that should have UNCTAD members (195 - all UN + observers)
FILES_WITH_UNCTAD_MEMBERS = [
    "UNCTAD.yaml",
]

# Files that should have ITC members (WTO + UN members)
FILES_WITH_ITC_MEMBERS = [
    "ITC.yaml",
]

def load_un_members():
    """Load UN member list from UN.yaml"""
    with open(UN_FILE, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('includes', []), data.get('membership_count', 193)

def update_file(filepath, members, membership_count):
    """Update a YAML file with includes data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Check if includes already exists
    if 'includes' in data and data['includes']:
        print(f"  {filepath.name} already has includes data, skipping...")
        return False
    
    # Add includes
    data['includes'] = members
    data['membership_count'] = membership_count
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"  ✓ Updated {filepath.name} with {membership_count} members")
    return True

def main():
    """Main function"""
    print("Loading UN member list...")
    un_members, un_count = load_un_members()
    print(f"  Found {un_count} UN members")
    
    # For UNCTAD, we use the same list (195 includes observers, but we'll use UN members)
    # For ITC, we also use UN members (it works with WTO and UN members)
    
    updated_count = 0
    
    # Update files with UN members
    print("\nUpdating files with UN member list...")
    for filename in FILES_WITH_UN_MEMBERS:
        filepath = UNAGENCY_DIR / filename
        if filepath.exists():
            if update_file(filepath, un_members, un_count):
                updated_count += 1
        else:
            print(f"  ⚠ File not found: {filename}")
    
    # Update UNCTAD
    print("\nUpdating UNCTAD...")
    for filename in FILES_WITH_UNCTAD_MEMBERS:
        filepath = UNAGENCY_DIR / filename
        if filepath.exists():
            # UNCTAD has 195 members (UN + observers), but we'll use UN members
            # Note: This is approximate as observers aren't in our UN.yaml
            if update_file(filepath, un_members, un_count):
                updated_count += 1
        else:
            print(f"  ⚠ File not found: {filename}")
    
    # Update ITC
    print("\nUpdating ITC...")
    for filename in FILES_WITH_ITC_MEMBERS:
        filepath = UNAGENCY_DIR / filename
        if filepath.exists():
            # ITC works with WTO and UN members, using UN members as base
            if update_file(filepath, un_members, un_count):
                updated_count += 1
        else:
            print(f"  ⚠ File not found: {filename}")
    
    print(f"\n✓ Updated {updated_count} files")

if __name__ == "__main__":
    main()
