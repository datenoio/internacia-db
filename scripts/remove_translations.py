#!/usr/bin/env python3
"""
Script to remove the 'translations' attribute from all intblock YAML files.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import typer

app = typer.Typer()


def remove_translations_from_file(file_path: Path) -> bool:
    """Remove translations field from a YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False
        
        # Check if translations field exists
        if 'translations' not in data:
            return False
        
        # Remove translations field
        del data['translations']
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return True
        
    except Exception as e:
        typer.echo(f"Error processing {file_path}: {e}", err=True)
        return False


@app.command()
def remove_all(
    intblocks_dir: Path = typer.Option(
        None,
        "--dir",
        help="Intblocks directory (default: data/intblocks)"
    )
):
    """Remove translations field from all intblock YAML files."""
    project_root = Path(__file__).parent.parent
    
    if intblocks_dir is None:
        intblocks_dir = project_root / "data" / "intblocks"
    
    if not intblocks_dir.exists():
        typer.echo(f"Error: Intblocks directory not found: {intblocks_dir}", err=True)
        raise typer.Exit(1)
    
    yaml_files = list(intblocks_dir.rglob("*.yaml"))
    
    typer.echo(f"Processing {len(yaml_files)} intblock files...")
    
    updated_count = 0
    for yaml_file in yaml_files:
        if remove_translations_from_file(yaml_file):
            updated_count += 1
    
    typer.echo(f"\n✅ Removed translations from {updated_count} files")


if __name__ == "__main__":
    app()

