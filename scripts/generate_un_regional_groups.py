#!/usr/bin/env python3
"""
Script to generate missing UN regional group YAML files.
"""

import os
import yaml
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "intblocks" / "unregionalblocks"

# Country mappings based on UN.yaml and web research
# Format: {country_name: (code, name_in_db)}

# African Group (54 countries)
AFRICAN_GROUP = [
    ("DZ", "Algeria"),
    ("AO", "Angola"),
    ("BJ", "Benin"),
    ("BW", "Botswana"),
    ("BF", "Burkina Faso"),
    ("BI", "Burundi"),
    ("CV", "Cabo Verde"),
    ("CM", "Cameroon"),
    ("CF", "Central African Republic"),
    ("TD", "Chad"),
    ("KM", "Comoros"),
    ("CG", "Congo"),
    ("CD", "Congo, The Democratic Republic of the"),
    ("DJ", "Djibouti"),
    ("EG", "Egypt, Arab Rep."),
    ("GQ", "Equatorial Guinea"),
    ("ER", "Eritrea"),
    ("SZ", "Eswatini"),
    ("ET", "Ethiopia"),
    ("GA", "Gabon"),
    ("GM", "Gambia"),
    ("GH", "Ghana"),
    ("GN", "Guinea"),
    ("GW", "Guinea-Bissau"),
    ("KE", "Kenya"),
    ("LS", "Lesotho"),
    ("LR", "Liberia"),
    ("LY", "Libya"),
    ("MG", "Madagascar"),
    ("MW", "Malawi"),
    ("ML", "Mali"),
    ("MR", "Mauritania"),
    ("MU", "Mauritius"),
    ("MA", "Morocco"),
    ("MZ", "Mozambique"),
    ("NA", "Namibia"),
    ("NE", "Niger"),
    ("NG", "Nigeria"),
    ("RW", "Rwanda"),
    ("ST", "Sao Tome and Principe"),
    ("SN", "Senegal"),
    ("SC", "Seychelles"),
    ("SL", "Sierra Leone"),
    ("SO", "Somalia"),
    ("ZA", "South Africa"),
    ("SS", "South Sudan"),
    ("SD", "Sudan"),
    ("TZ", "Tanzania, United Republic of"),
    ("TG", "Togo"),
    ("TN", "Tunisia"),
    ("UG", "Uganda"),
    ("ZM", "Zambia"),
    ("ZW", "Zimbabwe"),
]

# Asia-Pacific Group (54-58 countries)
ASIAPACIFIC_GROUP = [
    ("AF", "Afghanistan"),
    ("AM", "Armenia"),
    ("AU", "Australia"),
    ("AZ", "Azerbaijan"),
    ("BH", "Bahrain"),
    ("BD", "Bangladesh"),
    ("BT", "Bhutan"),
    ("BN", "Brunei Darussalam"),
    ("KH", "Cambodia"),
    ("CN", "China"),
    ("CY", "Cyprus"),
    ("KP", "Korea, Democratic People's Republic of"),
    ("FJ", "Fiji"),
    ("IN", "India"),
    ("ID", "Indonesia"),
    ("IR", "Iran, Islamic Republic of"),
    ("IQ", "Iraq"),
    ("JP", "Japan"),
    ("JO", "Jordan"),
    ("KZ", "Kazakhstan"),
    ("KI", "Kiribati"),
    ("KW", "Kuwait"),
    ("KG", "Kyrgyzstan"),
    ("LA", "Lao People's Democratic Republic"),
    ("LB", "Lebanon"),
    ("MY", "Malaysia"),
    ("MV", "Maldives"),
    ("MH", "Marshall Islands"),
    ("FM", "Micronesia, Federated States of"),
    ("MN", "Mongolia"),
    ("MM", "Myanmar"),
    ("NR", "Nauru"),
    ("NP", "Nepal"),
    ("NZ", "New Zealand"),
    ("OM", "Oman"),
    ("PK", "Pakistan"),
    ("PW", "Palau"),
    ("PG", "Papua New Guinea"),
    ("PH", "Philippines"),
    ("QA", "Qatar"),
    ("KR", "Korea, Republic of"),
    ("WS", "Samoa"),
    ("SA", "Saudi Arabia"),
    ("SG", "Singapore"),
    ("SB", "Solomon Islands"),
    ("LK", "Sri Lanka"),
    ("SY", "Syrian Arab Republic"),
    ("TJ", "Tajikistan"),
    ("TH", "Thailand"),
    ("TL", "Timor-Leste"),
    ("TO", "Tonga"),
    ("TM", "Turkmenistan"),
    ("TV", "Tuvalu"),
    ("AE", "United Arab Emirates"),
    ("UZ", "Uzbekistan"),
    ("VU", "Vanuatu"),
    ("VN", "Viet Nam"),
    ("YE", "Yemen"),
]

# Eastern European Group (23 countries)
EASTERN_EUROPEAN_GROUP = [
    ("AL", "Albania"),
    ("AM", "Armenia"),
    ("AZ", "Azerbaijan"),
    ("BY", "Belarus"),
    ("BA", "Bosnia and Herzegovina"),
    ("BG", "Bulgaria"),
    ("HR", "Croatia"),
    ("CZ", "Czechia"),
    ("EE", "Estonia"),
    ("GE", "Georgia"),
    ("HU", "Hungary"),
    ("LV", "Latvia"),
    ("LT", "Lithuania"),
    ("ME", "Montenegro"),
    ("MK", "North Macedonia"),
    ("MD", "Moldova, Republic of"),
    ("PL", "Poland"),
    ("RO", "Romania"),
    ("RU", "Russian Federation"),
    ("RS", "Serbia"),
    ("SK", "Slovakia"),
    ("SI", "Slovenia"),
    ("UA", "Ukraine"),
]

# GRULAC (33 countries)
GRULAC = [
    ("AG", "Antigua and Barbuda"),
    ("AR", "Argentina"),
    ("BS", "Bahamas"),
    ("BB", "Barbados"),
    ("BZ", "Belize"),
    ("BO", "Bolivia, Plurinational State of"),
    ("BR", "Brazil"),
    ("CL", "Chile"),
    ("CO", "Colombia"),
    ("CR", "Costa Rica"),
    ("CU", "Cuba"),
    ("DM", "Dominica"),
    ("DO", "Dominican Republic"),
    ("EC", "Ecuador"),
    ("SV", "El Salvador"),
    ("GD", "Grenada"),
    ("GT", "Guatemala"),
    ("GY", "Guyana"),
    ("HT", "Haiti"),
    ("HN", "Honduras"),
    ("JM", "Jamaica"),
    ("MX", "Mexico"),
    ("NI", "Nicaragua"),
    ("PA", "Panama"),
    ("PY", "Paraguay"),
    ("PE", "Peru"),
    ("KN", "Saint Kitts and Nevis"),
    ("LC", "Saint Lucia"),
    ("VC", "Saint Vincent and the Grenadines"),
    ("SR", "Suriname"),
    ("TT", "Trinidad and Tobago"),
    ("UY", "Uruguay"),
    ("VE", "Venezuela, Bolivarian Republic of"),
]

def create_yaml_file(group_id, group_name, members, wikidata_id=None, description=None):
    """Create a YAML file for a UN regional group."""
    
    includes = []
    for code, name in members:
        includes.append({
            "id": code,
            "name": name,
            "type": "country",
            "status": "member"
        })
    
    data = {
        "id": group_id,
        "blocktype": ["unregionalblock"],
        "status": "informal",
        "name": group_name,
        "includes": includes,
        "membership_count": len(members),
    }
    
    if wikidata_id:
        data["wikidata_id"] = wikidata_id
        data["links"] = [
            {"url": f"https://www.wikidata.org/wiki/{wikidata_id}", "type": "wikidata"}
        ]
    
    if description:
        data["description"] = description
    
    data["tags"] = [
        group_id,
        "cooperation",
        "political",
        "regional",
        "regional_cooperation",
        "unregionalblock",
    ]
    
    data["topics"] = [
        {"key": "political", "name": "Political"},
        {"key": "regional_cooperation", "name": "Regional Cooperation"}
    ]
    
    return data

def main():
    """Generate all missing UN regional group files."""
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Define groups
    groups = [
        {
            "id": "AFRICANGROUP",
            "name": "African Group",
            "members": AFRICAN_GROUP,
            "wikidata_id": "Q2820961",
            "description": "UN regional group comprising 54 African member states."
        },
        {
            "id": "ASIAPACIFICGROUP",
            "name": "Asia-Pacific Group",
            "members": ASIAPACIFIC_GROUP,
            "wikidata_id": "Q1060890",
            "description": "UN regional group comprising Asia-Pacific member states."
        },
        {
            "id": "EEG",
            "name": "Eastern European Group",
            "members": EASTERN_EUROPEAN_GROUP,
            "wikidata_id": "Q1279920",
            "description": "UN regional group comprising 23 Eastern European member states."
        },
        {
            "id": "GRULAC",
            "name": "Group of Latin American and Caribbean Countries",
            "members": GRULAC,
            "wikidata_id": "Q1060891",
            "description": "UN regional group comprising 33 Latin American and Caribbean member states."
        },
    ]
    
    for group in groups:
        data = create_yaml_file(
            group["id"],
            group["name"],
            group["members"],
            group.get("wikidata_id"),
            group.get("description")
        )
        
        output_file = OUTPUT_DIR / f"{group['id']}.yaml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        print(f"Created: {output_file} ({data['membership_count']} members)")

if __name__ == "__main__":
    main()
