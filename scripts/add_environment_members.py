#!/usr/bin/env python3
"""
Script to add member countries to environment international blocks.
Reads country files and generates membership lists.
"""

import yaml
from pathlib import Path
from typing import Dict, List

def get_country_name_mapping() -> Dict[str, str]:
    """Read all country files and create a mapping from code to standardized name."""
    countries_dir = Path(__file__).parent.parent / "data" / "countries"
    mapping = {}
    
    for country_file in sorted(countries_dir.glob("*.yaml")):
        with open(country_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            code = data.get('code', '')
            # Use official_name if available, otherwise use name
            name = data.get('official_name') or data.get('name', '')
            if code and name:
                mapping[code] = name
    
    # Special mappings for common variations
    special_mappings = {
        'KP': 'Korea, Democratic People\'s Republic of',
        'KR': 'Korea, Republic of',
        'EG': 'Egypt',
        'VE': 'Venezuela (Bolivarian Republic of)',
        'BO': 'Bolivia (Plurinational State of)',
        'FM': 'Micronesia (Federated States of)',
        'MD': 'Republic of Moldova',
        'MK': 'North Macedonia',
        'PS': 'Palestine, State of',
        'RU': 'Russian Federation',
        'TZ': 'United Republic of Tanzania',
        'GB': 'United Kingdom of Great Britain and Northern Ireland',
        'US': 'United States of America',
        'VN': 'Viet Nam',
        'TR': 'Türkiye',
    }
    
    # Override with special mappings
    for code, name in special_mappings.items():
        if code in mapping:
            mapping[code] = name
    
    return mapping

def generate_membership_list(country_codes: List[str], country_mapping: Dict[str, str]) -> List[Dict]:
    """Generate membership list from country codes."""
    members = []
    for code in sorted(country_codes):
        if code in country_mapping:
            members.append({
                'id': code,
                'name': country_mapping[code],
                'type': 'country',
                'status': 'member'
            })
        elif code == 'EU':
            members.append({
                'id': 'EU',
                'name': 'European Union',
                'type': 'organization',
                'status': 'member'
            })
        else:
            print(f"Warning: Country code {code} not found in mapping")
    return members

if __name__ == "__main__":
    country_mapping = get_country_name_mapping()
    print(f"Loaded {len(country_mapping)} countries")
    print("\nSample mappings:")
    for code in list(country_mapping.keys())[:10]:
        print(f"  {code}: {country_mapping[code]}")
