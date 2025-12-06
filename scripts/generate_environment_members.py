#!/usr/bin/env python3
"""
Script to generate membership lists for environment international blocks.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set

def get_country_name(code: str, country_data: Dict) -> str:
    """Get the appropriate country name for use in membership lists."""
    # Special cases that need full names
    special_names = {
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
        'CD': 'Democratic Republic of the Congo',
        'CG': 'Congo',
        'LA': 'Lao People\'s Democratic Republic',
        'SY': 'Syrian Arab Republic',
        'IR': 'Iran (Islamic Republic of)',
        'CI': 'Côte d\'Ivoire',
    }
    
    if code in special_names:
        return special_names[code]
    
    # Use the simple name field
    return country_data.get('name', '')

def load_all_countries() -> Dict[str, Dict]:
    """Load all country data."""
    countries_dir = Path(__file__).parent.parent / "data" / "countries"
    countries = {}
    
    for country_file in sorted(countries_dir.glob("*.yaml")):
        with open(country_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            code = data.get('code', '')
            if code:
                countries[code] = data
    
    return countries

def get_un_members(countries: Dict[str, Dict]) -> Set[str]:
    """Get all UN member countries."""
    un_members = set()
    for code, data in countries.items():
        if data.get('un_member', False):
            un_members.add(code)
    return un_members

def generate_membership_yaml(country_codes: List[str], countries: Dict[str, Dict]) -> str:
    """Generate YAML includes section for membership list."""
    lines = ["includes:"]
    
    # Sort by country code for consistency
    sorted_codes = sorted(country_codes)
    
    for code in sorted_codes:
        if code == 'EU':
            lines.append(f"- id: EU")
            lines.append(f"  name: European Union")
            lines.append(f"  type: organization")
            lines.append(f"  status: member")
        elif code in countries:
            name = get_country_name(code, countries[code])
            lines.append(f"- id: {code}")
            lines.append(f"  name: {name}")
            lines.append(f"  type: country")
            lines.append(f"  status: member")
        else:
            print(f"Warning: Country code {code} not found")
    
    return "\n".join(lines)

# UNFCCC has 198 parties: all UN members + Cook Islands, Niue, Palestine, Holy See, EU
def get_unfccc_members(countries: Dict[str, Dict]) -> List[str]:
    """Get UNFCCC membership (198 parties)."""
    un_members = get_un_members(countries)
    # Add non-UN members that are UNFCCC parties
    additional = {'CK', 'NU', 'PS', 'VA', 'EU'}  # Cook Islands, Niue, Palestine, Holy See, EU
    return sorted(list(un_members | additional))

# Vienna Convention and Montreal Protocol have the same 198 parties as UNFCCC
def get_vienna_montreal_members(countries: Dict[str, Dict]) -> List[str]:
    """Get Vienna Convention and Montreal Protocol membership (198 parties)."""
    return get_unfccc_members(countries)

# UNCCD has 197 parties: all UN members + Cook Islands, Niue, Palestine, EU (no Holy See)
def get_unccd_members(countries: Dict[str, Dict]) -> List[str]:
    """Get UNCCD membership (197 parties)."""
    un_members = get_un_members(countries)
    additional = {'CK', 'NU', 'PS', 'EU'}  # Cook Islands, Niue, Palestine, EU
    return sorted(list(un_members | additional))

# Paris Agreement has 194 parties (193 countries + EU)
# Excludes: Iran, Libya, Yemen (signed but not ratified), US withdrew in 2026
def get_paris_agreement_members(countries: Dict[str, Dict]) -> List[str]:
    """Get Paris Agreement membership (194 parties)."""
    un_members = get_un_members(countries)
    # Remove countries that haven't ratified: IR, LY, YE
    # Note: US is included as it was a party until 2026
    excluded = {'IR', 'LY', 'YE'}
    additional = {'EU'}
    return sorted(list((un_members - excluded) | additional))

# Kyoto Protocol has 192 parties
# Excludes: Andorra, Canada, South Sudan, United States
def get_kyoto_protocol_members(countries: Dict[str, Dict]) -> List[str]:
    """Get Kyoto Protocol membership (192 parties)."""
    un_members = get_un_members(countries)
    excluded = {'AD', 'CA', 'SS', 'US'}  # Andorra, Canada, South Sudan, US
    return sorted(list(un_members - excluded))

# CBD has 193 parties: all UN members except Andorra, South Sudan, US, Holy See
def get_cbd_members(countries: Dict[str, Dict]) -> List[str]:
    """Get CBD membership (193 parties)."""
    un_members = get_un_members(countries)
    excluded = {'AD', 'SS', 'US', 'VA'}  # Andorra, South Sudan, US, Holy See
    return sorted(list(un_members - excluded))

# CITES has 185 parties (184 countries + EU)
# Excludes: North Korea, Micronesia, Haiti, Kiribati, Marshall Islands, Nauru, South Sudan, East Timor, Tuvalu
def get_cites_members(countries: Dict[str, Dict]) -> List[str]:
    """Get CITES membership (185 parties)."""
    un_members = get_un_members(countries)
    excluded = {'KP', 'FM', 'HT', 'KI', 'MH', 'NR', 'SS', 'TL', 'TV'}
    additional = {'EU'}
    return sorted(list((un_members - excluded) | additional))

def write_membership_to_file(org_id: str, members: List[str], countries: Dict[str, Dict], output_dir: Path):
    """Write membership list to a file."""
    yaml_content = generate_membership_yaml(members, countries)
    output_file = output_dir / f"{org_id}_members.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    print(f"Written {len(members)} members to {output_file}")

if __name__ == "__main__":
    countries = load_all_countries()
    print(f"Loaded {len(countries)} countries")
    
    # Check for special countries
    print(f"\nChecking special countries:")
    for code in ['CK', 'NU', 'PS', 'VA']:
        if code in countries:
            print(f"  {code}: {countries[code].get('name', 'N/A')}")
        else:
            print(f"  {code}: NOT FOUND")
    
    # Generate membership lists
    print("\nGenerating membership lists...")
    
    output_dir = Path(__file__).parent.parent / "data" / "intblocks" / "environment"
    
    unfccc = get_unfccc_members(countries)
    print(f"UNFCCC: {len(unfccc)} members")
    write_membership_to_file("UNFCCC", unfccc, countries, output_dir)
    
    vienna_montreal = get_vienna_montreal_members(countries)
    print(f"Vienna/Montreal: {len(vienna_montreal)} members")
    write_membership_to_file("VIENNACONVENTION", vienna_montreal, countries, output_dir)
    write_membership_to_file("MONTREALPROTOCOL", vienna_montreal, countries, output_dir)
    
    unccd = get_unccd_members(countries)
    print(f"UNCCD: {len(unccd)} members")
    write_membership_to_file("UNCCD", unccd, countries, output_dir)
    
    paris = get_paris_agreement_members(countries)
    print(f"Paris Agreement: {len(paris)} members")
    write_membership_to_file("PARISAGREEMENT", paris, countries, output_dir)
    
    kyoto = get_kyoto_protocol_members(countries)
    print(f"Kyoto Protocol: {len(kyoto)} members")
    write_membership_to_file("KYOTOPROTOCOL", kyoto, countries, output_dir)
    
    cbd = get_cbd_members(countries)
    print(f"CBD: {len(cbd)} members")
    write_membership_to_file("CBD", cbd, countries, output_dir)
    
    cites = get_cites_members(countries)
    print(f"CITES: {len(cites)} members")
    write_membership_to_file("CITES", cites, countries, output_dir)
