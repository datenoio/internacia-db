#!/usr/bin/env python3
"""
Dataset builder for Internacia project.

This script generates datasets from data/countries and data/intblocks directories
in multiple formats: JSONL (zstd), YAML (zstd), Parquet (zstd), and DuckDB database.
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any
import typer
from tqdm import tqdm
import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import zstandard as zstd

app = typer.Typer(help="Dataset builder for Internacia project")


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_countries_schema() -> pa.Schema:
    """Define explicit PyArrow schema for countries."""
    return pa.schema([
        ('code', pa.string()),
        ('name', pa.string()),
        ('iso3code', pa.string()),
        ('capital_city', pa.struct([
            ('name', pa.string()),
            ('lng', pa.float64()),
            ('lat', pa.float64())
        ])),
        ('region', pa.struct([
            ('id', pa.string()),
            ('value', pa.string())
        ])),
        ('adminregion', pa.struct([
            ('id', pa.string()),
            ('value', pa.string())
        ])),
        ('incomeLevel', pa.struct([
            ('id', pa.string()),
            ('value', pa.string())
        ])),
        ('lendingType', pa.struct([
            ('id', pa.string()),
            ('value', pa.string())
        ])),
        ('numeric_code', pa.string()),
        ('wikidata_id', pa.string()),
        ('official_name', pa.string()),
        ('languages', pa.list_(pa.struct([
            ('code', pa.string()),
            ('name', pa.string()),
            ('official', pa.bool_())
        ]))),
        ('currencies', pa.list_(pa.struct([
            ('code', pa.string()),
            ('name', pa.string()),
            ('symbol', pa.string())
        ]))),
        ('un_member', pa.bool_()),
        ('independent', pa.bool_()),
        ('subregion', pa.string()),
        ('continents', pa.list_(pa.string())),
        ('borders', pa.list_(pa.string())),
        ('landlocked', pa.bool_()),
        ('tld', pa.string()),
        ('calling_codes', pa.list_(pa.string())),
        ('flag_emoji', pa.string()),
        ('car_side', pa.string()),
        ('start_of_week', pa.string()),
        ('demonyms', pa.struct([
            ('female', pa.string()),
            ('male', pa.string())
        ])),
        ('m49_code', pa.string()),
        ('population', pa.int64()),
        ('area', pa.float64()),
        ('gini', pa.struct([
            ('year', pa.int64()),
            ('value', pa.float64())
        ])),
        ('timezones', pa.list_(pa.string())),
        ('native_names', pa.map_(pa.string(), pa.struct([
            ('official', pa.string()),
            ('common', pa.string())
        ]))),
        ('other_names', pa.list_(pa.struct([
            ('id', pa.string()),
            ('name', pa.string())
        ]))),
        ('common_names', pa.list_(pa.string()))
    ])


def get_intblocks_schema() -> pa.Schema:
    """Define explicit PyArrow schema for intblocks."""
    return pa.schema([
        ('id', pa.string()),
        ('blocktype', pa.list_(pa.string())),
        ('status', pa.string()),
        ('name', pa.string()),
        ('languages', pa.list_(pa.string())),
        ('links', pa.list_(pa.struct([
            ('url', pa.string()),
            ('type', pa.string())
        ]))),
        ('translations', pa.list_(pa.struct([
            ('lang', pa.string()),
            ('name', pa.string())
        ]))),
        ('founded', pa.string()),
        ('geographic_scope', pa.string()),
        ('regions', pa.list_(pa.string())),
        ('includes', pa.list_(pa.struct([
            ('id', pa.string()),
            ('name', pa.string()),
            ('type', pa.string()),
            ('status', pa.string()),
            ('joined', pa.string()),
            ('role', pa.string()),
            ('note', pa.string())
        ]))),
        ('membership_count', pa.int64()),
        ('wikidata_id', pa.string()),
        ('legal_status', pa.string()),
        ('description', pa.string()),
        ('tags', pa.list_(pa.string())),
        ('topics', pa.list_(pa.struct([
            ('key', pa.string()),
            ('name', pa.string())
        ]))),
        ('headquarters', pa.struct([
            ('city', pa.string()),
            ('country', pa.string()),
            ('coordinates', pa.struct([
                ('lat', pa.float64()),
                ('lng', pa.float64())
            ]))
        ])),
        ('acronyms', pa.list_(pa.struct([
            ('lang', pa.string()),
            ('value', pa.string())
        ]))),
        ('partof', pa.list_(pa.string())),  # Normalized to list of strings
        ('dissolved', pa.string()),
        ('predecessor', pa.string()),
        ('successor', pa.string()),
        ('other_names', pa.list_(pa.struct([
            ('id', pa.string()),
            ('name', pa.string())
        ])))
    ])


def get_blocktypes_schema() -> pa.Schema:
    """Define explicit PyArrow schema for blocktypes."""
    return pa.schema([
        ('id', pa.string()),
        ('name', pa.string()),
        ('other_names', pa.list_(pa.struct([
            ('lang', pa.string()),
            ('name', pa.string())
        ])))
    ])


def clean_data(data: List[Dict[str, Any]], dataset_type: str) -> List[Dict[str, Any]]:
    """
    Clean data to ensure consistency with schema.
    
    Fixes known issues:
    - Boolean 'lang' values (from 'no' parsed as False) -> converted to "no"
    - Inconsistent 'partof' field -> normalized to list of strings
    - Boolean values in string fields -> converted to strings
    - None values in required string fields -> converted to empty strings
    """
    cleaned_data = []
    
    # String fields that should never be None or bool
    string_fields = {
        'id', 'status', 'name', 'founded', 'geographic_scope', 'wikidata_id', 
        'legal_status', 'description', 'dissolved', 'predecessor', 'successor'
    }
    
    for item in data:
        # Deep copy to avoid modifying original if needed, but for now just modifying dict
        cleaned_item = item.copy()
        
        if dataset_type == 'intblocks':
            # Fix boolean languages in translations
            if 'translations' in cleaned_item:
                new_translations = []
                for t in cleaned_item['translations']:
                    if isinstance(t, dict):
                        new_t = t.copy()
                        if 'lang' in new_t and isinstance(new_t['lang'], bool):
                            new_t['lang'] = "no" if new_t['lang'] is False else "yes"
                        if 'name' in new_t and isinstance(new_t['name'], bool):
                            new_t['name'] = "no" if new_t['name'] is False else "yes"
                        new_translations.append(new_t)
                cleaned_item['translations'] = new_translations
            
            # Fix boolean languages list
            if 'languages' in cleaned_item:
                new_languages = []
                for l in cleaned_item['languages']:
                    if isinstance(l, bool):
                        new_languages.append("no" if l is False else "yes")
                    else:
                        new_languages.append(str(l))
                cleaned_item['languages'] = new_languages

            # Normalize partof to list of strings
            if 'partof' in cleaned_item:
                partof = cleaned_item['partof']
                if partof is None:
                    cleaned_item['partof'] = []
                elif isinstance(partof, str):
                    cleaned_item['partof'] = [partof]
                elif isinstance(partof, dict):
                    # If it's a dict, it might be an ID->Name map or similar
                    # For now, let's just take keys if they look like IDs
                    cleaned_item['partof'] = list(partof.keys())
                elif isinstance(partof, list):
                    # Ensure all items are strings
                    cleaned_item['partof'] = [str(p) for p in partof]
            
            # Fix boolean values in string fields
            for field in string_fields:
                if field in cleaned_item:
                    if isinstance(cleaned_item[field], bool):
                        cleaned_item[field] = "yes" if cleaned_item[field] else "no"
                    elif cleaned_item[field] is None:
                        cleaned_item[field] = ""
            
            # Ensure includes fields are strings
            if 'includes' in cleaned_item:
                for member in cleaned_item['includes']:
                    if isinstance(member, dict):
                        for key in ['id', 'name', 'type', 'status', 'joined', 'role', 'note']:
                            if key in member:
                                if isinstance(member[key], bool):
                                    member[key] = "yes" if member[key] else "no"
                                elif member[key] is None:
                                    member[key] = ""
            
            # Ensure links fields are strings
            if 'links' in cleaned_item:
                for link in cleaned_item['links']:
                    if isinstance(link, dict):
                        for key in ['url', 'type']:
                            if key in link:
                                if isinstance(link[key], bool):
                                    link[key] = "yes" if link[key] else "no"
                                elif link[key] is None:
                                    link[key] = ""
            
            # Ensure other_names fields are strings
            if 'other_names' in cleaned_item:
                for name in cleaned_item['other_names']:
                    if isinstance(name, dict):
                        for key in ['id', 'name']:
                            if key in name:
                                if isinstance(name[key], bool):
                                    name[key] = "yes" if name[key] else "no"
                                elif name[key] is None:
                                    name[key] = ""
            
            # Ensure acronyms fields are strings
            if 'acronyms' in cleaned_item:
                for acronym in cleaned_item['acronyms']:
                    if isinstance(acronym, dict):
                        for key in ['lang', 'value']:
                            if key in acronym:
                                if isinstance(acronym[key], bool):
                                    acronym[key] = "yes" if acronym[key] else "no"
                                elif acronym[key] is None:
                                    acronym[key] = ""
            
            # Ensure headquarters fields are strings/floats
            if 'headquarters' in cleaned_item:
                hq = cleaned_item['headquarters']
                if isinstance(hq, dict):
                    for key in ['city', 'country']:
                        if key in hq:
                            if isinstance(hq[key], bool):
                                hq[key] = "yes" if hq[key] else "no"
                            elif hq[key] is None:
                                hq[key] = ""
                    if 'coordinates' in hq and isinstance(hq['coordinates'], dict):
                        for key in ['lat', 'lng']:
                            if key in hq['coordinates']:
                                if isinstance(hq['coordinates'][key], bool):
                                    hq['coordinates'][key] = 0.0
                                elif hq['coordinates'][key] is None:
                                    hq['coordinates'][key] = 0.0
            
            # Ensure topics fields are strings
            if 'topics' in cleaned_item:
                for topic in cleaned_item['topics']:
                    if isinstance(topic, dict):
                        for key in ['key', 'name']:
                            if key in topic:
                                if isinstance(topic[key], bool):
                                    topic[key] = "yes" if topic[key] else "no"
                                elif topic[key] is None:
                                    topic[key] = ""
        
        if dataset_type == 'blocktypes':
            # Ensure other_names fields are strings
            if 'other_names' in cleaned_item:
                if cleaned_item['other_names'] is None:
                    cleaned_item['other_names'] = []
                elif isinstance(cleaned_item['other_names'], list):
                    for name in cleaned_item['other_names']:
                        if isinstance(name, dict):
                            for key in ['lang', 'name']:
                                if key in name:
                                    if isinstance(name[key], bool):
                                        name[key] = "yes" if name[key] else "no"
                                    elif name[key] is None:
                                        name[key] = ""
            # Ensure id and name are strings
            for field in ['id', 'name']:
                if field in cleaned_item:
                    if isinstance(cleaned_item[field], bool):
                        cleaned_item[field] = "yes" if cleaned_item[field] else "no"
                    elif cleaned_item[field] is None:
                        cleaned_item[field] = ""
        
        cleaned_data.append(cleaned_item)
        
    return cleaned_data


def load_yaml_files(directory: Path, desc: str = "Loading files") -> List[Dict[str, Any]]:
    """Load all YAML files from a directory (including subdirectories)."""
    yaml_files = list(directory.rglob("*.yaml"))
    data = []
    
    for yaml_file in tqdm(yaml_files, desc=desc):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                if content:
                    data.append(content)
        except Exception as e:
            typer.echo(f"Error loading {yaml_file}: {e}", err=True)
    
    return data


def save_jsonl_zst(data: List[Dict[str, Any]], output_file: Path):
    """Save data as Zstandard-compressed JSONL file."""
    cctx = zstd.ZstdCompressor(level=22)
    with open(output_file, 'wb') as f:
        with cctx.stream_writer(f) as compressor:
            for item in data:
                line = json.dumps(item, ensure_ascii=False) + '\n'
                compressor.write(line.encode('utf-8'))
    typer.echo(f"✓ Saved JSONL (zstd): {output_file}")


def save_yaml_zst(data: List[Dict[str, Any]], output_file: Path):
    """Save data as Zstandard-compressed YAML file."""
    cctx = zstd.ZstdCompressor(level=22)
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    with open(output_file, 'wb') as f:
        f.write(cctx.compress(yaml_str.encode('utf-8')))
    typer.echo(f"✓ Saved YAML (zstd): {output_file}")


def save_parquet(data: List[Dict[str, Any]], output_file: Path, schema: pa.Schema = None):
    """Save data as Parquet file using explicit schema and Zstd compression."""
    try:
        # Convert to PyArrow Table using explicit schema
        # This will enforce types and handle nested structures correctly
        table = pa.Table.from_pylist(data, schema=schema)
        # Use high compression level for Zstd
        pq.write_table(table, output_file, compression='zstd', compression_level=22)
        typer.echo(f"✓ Saved Parquet (zstd): {output_file}")
    except Exception as e:
        typer.echo(f"Error saving Parquet {output_file}: {e}", err=True)
        # Fallback to pandas inference if schema fails (should not happen with correct schema)
        try:
            df = pd.DataFrame(data)
            df.to_parquet(output_file, engine='pyarrow', index=False, compression='zstd', compression_level=22)
            typer.echo(f"✓ Saved Parquet (fallback, zstd): {output_file}")
        except Exception as e2:
            typer.echo(f"Fallback failed: {e2}", err=True)


def create_duckdb_database(
    countries_data: List[Dict[str, Any]], 
    intblocks_data: List[Dict[str, Any]], 
    blocktypes_data: List[Dict[str, Any]],
    output_file: Path,
    countries_schema: pa.Schema,
    intblocks_schema: pa.Schema,
    blocktypes_schema: pa.Schema
):
    """Create DuckDB database with countries, intblocks, and blocktypes tables."""
    # Remove existing database if it exists
    if output_file.exists():
        output_file.unlink()
    
    # Connect to DuckDB
    con = duckdb.connect(str(output_file))
    
    try:
        # Create countries table
        typer.echo("Creating countries table...")
        countries_table = pa.Table.from_pylist(countries_data, schema=countries_schema)
        con.execute("CREATE TABLE countries AS SELECT * FROM countries_table")
        
        # Create intblocks table
        typer.echo("Creating intblocks table...")
        intblocks_table = pa.Table.from_pylist(intblocks_data, schema=intblocks_schema)
        con.execute("CREATE TABLE intblocks AS SELECT * FROM intblocks_table")
        
        # Create blocktypes table
        typer.echo("Creating blocktypes table...")
        blocktypes_table = pa.Table.from_pylist(blocktypes_data, schema=blocktypes_schema)
        con.execute("CREATE TABLE blocktypes AS SELECT * FROM blocktypes_table")
        
        # Get row counts
        countries_count = con.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
        intblocks_count = con.execute("SELECT COUNT(*) FROM intblocks").fetchone()[0]
        blocktypes_count = con.execute("SELECT COUNT(*) FROM blocktypes").fetchone()[0]
        
        typer.echo(f"✓ Saved DuckDB: {output_file}")
        typer.echo(f"  - Countries: {countries_count} rows")
        typer.echo(f"  - Intblocks: {intblocks_count} rows")
        typer.echo(f"  - Blocktypes: {blocktypes_count} rows")
        
    finally:
        con.close()


@app.command()
def build(
    output_dir: Path = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for datasets (default: data/datasets)"
    ),
    formats: str = typer.Option(
        "jsonl,yaml,parquet,duckdb",
        "--formats",
        "-f",
        help="Comma-separated list of formats to generate (jsonl, yaml, parquet, duckdb)"
    )
):
    """
    Build datasets from data/countries, data/intblocks directories, and data/datasets/blocktypes.yaml.
    
    Generates datasets in multiple formats:
    - JSONL: Zstd-compressed line-delimited JSON
    - YAML: Zstd-compressed YAML
    - Parquet: Zstd-compressed Parquet with explicit schema
    - DuckDB: Database with countries, intblocks, and blocktypes tables
    """
    project_root = get_project_root()
    
    # Set default output directory
    if output_dir is None:
        output_dir = project_root / "data" / "datasets"
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse formats
    requested_formats = [f.strip().lower() for f in formats.split(",")]
    valid_formats = {"jsonl", "yaml", "parquet", "duckdb"}
    invalid_formats = set(requested_formats) - valid_formats
    
    if invalid_formats:
        typer.echo(f"Error: Invalid formats: {', '.join(invalid_formats)}", err=True)
        typer.echo(f"Valid formats: {', '.join(valid_formats)}")
        raise typer.Exit(1)
    
    typer.echo(f"\n🚀 Building datasets...")
    typer.echo(f"Output directory: {output_dir}\n")
    
    # Load countries data
    countries_dir = project_root / "data" / "countries"
    if not countries_dir.exists():
        typer.echo(f"Error: Countries directory not found: {countries_dir}", err=True)
        raise typer.Exit(1)
    
    typer.echo("📁 Loading countries data...")
    countries_data = load_yaml_files(countries_dir, "Loading countries")
    typer.echo(f"   Loaded {len(countries_data)} countries")
    
    # Clean countries data (not strictly needed for now but good practice)
    countries_data = clean_data(countries_data, 'countries')
    
    # Load intblocks data
    intblocks_dir = project_root / "data" / "intblocks"
    if not intblocks_dir.exists():
        typer.echo(f"Error: Intblocks directory not found: {intblocks_dir}", err=True)
        raise typer.Exit(1)
    
    typer.echo("📁 Loading intblocks data...")
    intblocks_data = load_yaml_files(intblocks_dir, "Loading intblocks")
    typer.echo(f"   Loaded {len(intblocks_data)} intblocks")
    
    # Clean intblocks data
    typer.echo("🧹 Cleaning data...")
    intblocks_data = clean_data(intblocks_data, 'intblocks')
    
    # Load blocktypes data
    blocktypes_file = project_root / "data" / "datasets" / "blocktypes.yaml"
    if not blocktypes_file.exists():
        typer.echo(f"Error: Blocktypes file not found: {blocktypes_file}", err=True)
        raise typer.Exit(1)
    
    typer.echo("📁 Loading blocktypes data...")
    try:
        with open(blocktypes_file, 'r', encoding='utf-8') as f:
            blocktypes_data = yaml.safe_load(f)
            if blocktypes_data is None:
                blocktypes_data = []
            elif not isinstance(blocktypes_data, list):
                typer.echo(f"Warning: blocktypes.yaml should contain a list, got {type(blocktypes_data)}", err=True)
                blocktypes_data = []
    except Exception as e:
        typer.echo(f"Error loading {blocktypes_file}: {e}", err=True)
        raise typer.Exit(1)
    
    typer.echo(f"   Loaded {len(blocktypes_data)} blocktypes")
    
    # Clean blocktypes data
    blocktypes_data = clean_data(blocktypes_data, 'blocktypes')
    
    # Get schemas
    countries_schema = get_countries_schema()
    intblocks_schema = get_intblocks_schema()
    blocktypes_schema = get_blocktypes_schema()
    
    # Generate datasets
    typer.echo("\n💾 Generating datasets...\n")
    
    # Generate for countries
    if "jsonl" in requested_formats:
        save_jsonl_zst(countries_data, output_dir / "countries.jsonl.zst")
        save_jsonl_zst(intblocks_data, output_dir / "intblocks.jsonl.zst")
        save_jsonl_zst(blocktypes_data, output_dir / "blocktypes.jsonl.zst")
    
    if "yaml" in requested_formats:
        save_yaml_zst(countries_data, output_dir / "countries.yaml.zst")
        save_yaml_zst(intblocks_data, output_dir / "intblocks.yaml.zst")
        save_yaml_zst(blocktypes_data, output_dir / "blocktypes.yaml.zst")
    
    if "parquet" in requested_formats:
        save_parquet(countries_data, output_dir / "countries.parquet", schema=countries_schema)
        save_parquet(intblocks_data, output_dir / "intblocks.parquet", schema=intblocks_schema)
        save_parquet(blocktypes_data, output_dir / "blocktypes.parquet", schema=blocktypes_schema)
    
    if "duckdb" in requested_formats:
        create_duckdb_database(
            countries_data, 
            intblocks_data,
            blocktypes_data,
            output_dir / "internacia.duckdb",
            countries_schema=countries_schema,
            intblocks_schema=intblocks_schema,
            blocktypes_schema=blocktypes_schema
        )
    
    typer.echo(f"\n✅ All datasets generated successfully!")
    typer.echo(f"📂 Output location: {output_dir}")


@app.command()
def info():
    """Display information about the builder and available data sources."""
    project_root = get_project_root()
    
    typer.echo("\n📊 Internacia Dataset Builder\n")
    typer.echo("Data sources:")
    
    countries_dir = project_root / "data" / "countries"
    if countries_dir.exists():
        country_files = list(countries_dir.rglob("*.yaml"))
        typer.echo(f"  • Countries: {len(country_files)} files in {countries_dir}")
    else:
        typer.echo(f"  • Countries: ❌ Not found at {countries_dir}")
    
    intblocks_dir = project_root / "data" / "intblocks"
    if intblocks_dir.exists():
        intblock_files = list(intblocks_dir.rglob("*.yaml"))
        subdirs = [d for d in intblocks_dir.iterdir() if d.is_dir()]
        typer.echo(f"  • Intblocks: {len(intblock_files)} files in {intblocks_dir}")
        typer.echo(f"    Categories: {', '.join([d.name for d in subdirs])}")
    else:
        typer.echo(f"  • Intblocks: ❌ Not found at {intblocks_dir}")
    
    typer.echo("\nSupported formats:")
    typer.echo("  • JSONL - Zstd-compressed line-delimited JSON")
    typer.echo("  • YAML - Zstd-compressed YAML")
    typer.echo("  • Parquet - Zstd-compressed columnar format")
    typer.echo("  • DuckDB - Relational database with SQL support")
    typer.echo()


if __name__ == "__main__":
    app()
