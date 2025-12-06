#!/usr/bin/env python3
"""
Validate all YAML files in the data directory.
"""

import yaml
from pathlib import Path
from typing import List, Tuple
import typer

app = typer.Typer()


def validate_yaml_file(file_path: Path) -> Tuple[bool, str]:
    """Validate a single YAML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None:
                return False, "File is empty or contains only null"
            return True, ""
    except yaml.YAMLError as e:
        return False, f"YAML error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


@app.command()
def validate(
    directory: Path = typer.Argument(..., help="Directory to validate"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show all files")
):
    """Validate all YAML files in a directory."""
    if not directory.exists():
        typer.echo(f"Error: Directory not found: {directory}", err=True)
        raise typer.Exit(1)
    
    yaml_files = list(directory.rglob("*.yaml"))
    typer.echo(f"Validating {len(yaml_files)} YAML files in {directory}...\n")
    
    errors = []
    valid_count = 0
    
    for yaml_file in yaml_files:
        is_valid, error_msg = validate_yaml_file(yaml_file)
        if is_valid:
            valid_count += 1
            if verbose:
                typer.echo(f"✓ {yaml_file.relative_to(directory)}")
        else:
            errors.append((yaml_file, error_msg))
            typer.echo(f"✗ {yaml_file.relative_to(directory)}: {error_msg}", err=True)
    
    typer.echo(f"\n{'='*60}")
    typer.echo(f"Validation Results:")
    typer.echo(f"  Valid: {valid_count}/{len(yaml_files)}")
    typer.echo(f"  Errors: {len(errors)}/{len(yaml_files)}")
    
    if errors:
        typer.echo(f"\nFiles with errors:")
        for file_path, error in errors:
            typer.echo(f"  - {file_path.relative_to(directory)}: {error}")
        raise typer.Exit(1)
    else:
        typer.echo("\n✅ All files are valid!")
        return 0


if __name__ == "__main__":
    app()

