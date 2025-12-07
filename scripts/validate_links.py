#!/usr/bin/env python3
"""
Validate all links and wikidata_id values in intblocks YAML files.
"""

import yaml
import re
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import typer
from urllib.parse import urlparse
import time

app = typer.Typer()

# Rate limiting for HTTP requests
REQUEST_DELAY = 0.1  # seconds between requests
WIKIDATA_API_BASE = "https://www.wikidata.org/w/api.php"

# Session for connection pooling
session = requests.Session()
session.headers.update({
    'User-Agent': 'Internacia-DB Link Validator/1.0'
})


def extract_wikidata_id(url: str) -> Optional[str]:
    """Extract Q-number from a wikidata URL."""
    match = re.search(r'Q\d+', url)
    return match.group(0) if match else None


def validate_url(url: str, timeout: int = 10) -> Tuple[bool, str, int]:
    """
    Validate a URL by checking if it's accessible.
    Returns (is_valid, error_message, status_code)
    """
    try:
        # Skip validation for certain URL patterns that might be problematic
        parsed = urlparse(url)
        
        # Check for malformed URLs
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format", 0
        
        # For wikidata URLs, we'll validate via API instead
        if 'wikidata.org' in url:
            return True, "", 200  # Will validate separately via API
        
        # For wikipedia URLs, check if they're accessible
        if 'wikipedia.org' in url:
            try:
                response = session.head(url, allow_redirects=True, timeout=timeout)
                status = response.status_code
                if status == 200 or (300 <= status < 400):
                    return True, "", status
                else:
                    return False, f"HTTP {status}", status
            except requests.exceptions.RequestException as e:
                return False, str(e), 0
        
        # For other URLs, try HEAD first, then GET if needed
        try:
            response = session.head(url, allow_redirects=True, timeout=timeout)
            status = response.status_code
            if status == 200 or (300 <= status < 400):
                return True, "", status
            # Some servers don't support HEAD, try GET
            if status == 405:
                response = session.get(url, allow_redirects=True, timeout=timeout, stream=True)
                status = response.status_code
                if status == 200 or (300 <= status < 400):
                    return True, "", status
                else:
                    return False, f"HTTP {status}", status
            else:
                return False, f"HTTP {status}", status
        except requests.exceptions.Timeout:
            return False, "Request timeout", 0
        except requests.exceptions.ConnectionError:
            return False, "Connection error", 0
        except requests.exceptions.RequestException as e:
            return False, str(e), 0
            
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", 0


def get_wikidata_entity_info(qid: str) -> Tuple[bool, Optional[Dict]]:
    """
    Fetch information about a Wikidata entity.
    Returns (success, entity_data)
    """
    try:
        params = {
            'action': 'wbgetentities',
            'ids': qid,
            'format': 'json',
            'props': 'labels|descriptions|claims',
            'languages': 'en'
        }
        
        response = session.get(WIKIDATA_API_BASE, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'entities' in data and qid in data['entities']:
            entity = data['entities'][qid]
            if 'missing' in entity:
                return False, None
            return True, entity
        
        return False, None
    except Exception as e:
        return False, None


def validate_wikidata_entity(qid: str, entity_name: str) -> Tuple[bool, str]:
    """
    Validate that a Wikidata entity exists and matches the entity name.
    Returns (is_valid, error_message)
    """
    success, entity_data = get_wikidata_entity_info(qid)
    
    if not success or not entity_data:
        return False, f"Entity {qid} not found in Wikidata"
    
    # Get English label
    labels = entity_data.get('labels', {})
    en_label = labels.get('en', {}).get('value', '') if labels else ''
    
    # Check if the entity name is similar to the Wikidata label
    # We'll do a simple check - the entity name should be somewhat similar
    # This is a heuristic, not perfect
    if en_label:
        # Normalize for comparison (lowercase, remove extra spaces)
        normalized_en = ' '.join(en_label.lower().split())
        normalized_name = ' '.join(entity_name.lower().split())
        
        # Check if names are similar (contain common words or are very similar)
        # This is a basic check - could be improved
        if normalized_en == normalized_name:
            return True, ""
        # Check if one contains the other (for acronyms or variations)
        if normalized_name in normalized_en or normalized_en in normalized_name:
            return True, ""
        # Check for significant word overlap
        name_words = set(normalized_name.split())
        label_words = set(normalized_en.split())
        if len(name_words) > 0 and len(label_words) > 0:
            overlap = len(name_words & label_words) / max(len(name_words), len(label_words))
            if overlap > 0.3:  # 30% word overlap
                return True, ""
        
        return False, f"Name mismatch: Wikidata label is '{en_label}', entity name is '{entity_name}'"
    
    return True, ""  # If no English label, we can't verify but entity exists


def validate_yaml_file(file_path: Path, check_http: bool = True, check_wikidata: bool = True) -> Tuple[bool, List[str]]:
    """
    Validate links and wikidata_id in a YAML file.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return False, ["File is empty or contains only null"]
        
        entity_id = data.get('id', 'UNKNOWN')
        entity_name = data.get('name', '')
        
        # Validate links
        links = data.get('links', [])
        wikidata_ids_in_links = []
        
        for i, link in enumerate(links):
            if not isinstance(link, dict):
                errors.append(f"Link {i+1}: Invalid format (not a dictionary)")
                continue
            
            url = link.get('url', '')
            link_type = link.get('type', '')
            
            if not url:
                errors.append(f"Link {i+1}: Missing URL")
                continue
            
            if not link_type:
                errors.append(f"Link {i+1}: Missing type")
                continue
            
            # Extract wikidata ID from wikidata links
            if link_type == 'wikidata':
                qid = extract_wikidata_id(url)
                if qid:
                    wikidata_ids_in_links.append(qid)
                else:
                    errors.append(f"Link {i+1} (wikidata): Could not extract Q-number from URL: {url}")
            
            # Validate URL accessibility
            if check_http:
                is_valid, error_msg, status_code = validate_url(url)
                if not is_valid:
                    errors.append(f"Link {i+1} ({link_type}): {error_msg} - {url}")
                time.sleep(REQUEST_DELAY)  # Rate limiting
        
        # Validate wikidata_id field
        wikidata_id = data.get('wikidata_id')
        
        if wikidata_id:
            # Check format
            if not re.match(r'^Q\d+$', wikidata_id):
                errors.append(f"wikidata_id has invalid format: {wikidata_id}")
            else:
                # Check consistency with wikidata links
                if wikidata_ids_in_links:
                    if wikidata_id not in wikidata_ids_in_links:
                        errors.append(f"wikidata_id ({wikidata_id}) doesn't match any wikidata link Q-numbers: {wikidata_ids_in_links}")
                
                # Validate entity exists and matches name
                if check_wikidata and entity_name:
                    is_valid, error_msg = validate_wikidata_entity(wikidata_id, entity_name)
                    if not is_valid:
                        errors.append(f"wikidata_id validation: {error_msg}")
                    time.sleep(REQUEST_DELAY)  # Rate limiting
        
        # Check if there are wikidata links but no wikidata_id field
        if wikidata_ids_in_links and not wikidata_id:
            errors.append(f"Has wikidata link(s) but no wikidata_id field. Q-numbers found: {wikidata_ids_in_links}")
        
    except yaml.YAMLError as e:
        return False, [f"YAML error: {str(e)}"]
    except Exception as e:
        return False, [f"Error: {str(e)}"]
    
    return len(errors) == 0, errors


@app.command()
def validate(
    directory: Path = typer.Argument(
        default=Path("data/intblocks"),
        help="Directory containing intblocks YAML files"
    ),
    check_http: bool = typer.Option(
        True,
        "--check-http/--no-check-http",
        help="Check if URLs are accessible via HTTP"
    ),
    check_wikidata: bool = typer.Option(
        True,
        "--check-wikidata/--no-check-wikidata",
        help="Validate Wikidata entities match organization names"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output for each file"
    ),
    max_errors: int = typer.Option(
        100,
        "--max-errors",
        help="Maximum number of errors to display"
    )
):
    """Validate all links and wikidata_id values in intblocks YAML files."""
    directory = Path(directory)
    
    if not directory.exists():
        typer.echo(f"Error: Directory not found: {directory}", err=True)
        raise typer.Exit(1)
    
    yaml_files = sorted(directory.rglob("*.yaml"))
    typer.echo(f"Validating {len(yaml_files)} YAML files in {directory}...")
    typer.echo(f"  - HTTP validation: {'enabled' if check_http else 'disabled'}")
    typer.echo(f"  - Wikidata validation: {'enabled' if check_wikidata else 'disabled'}")
    typer.echo()
    
    valid_count = 0
    invalid_count = 0
    all_errors = []
    
    for i, yaml_file in enumerate(yaml_files, 1):
        if verbose:
            typer.echo(f"[{i}/{len(yaml_files)}] Checking {yaml_file.name}...", nl=False)
        
        is_valid, errors = validate_yaml_file(yaml_file, check_http, check_wikidata)
        
        if is_valid:
            valid_count += 1
            if verbose:
                typer.echo(" ✓")
        else:
            invalid_count += 1
            file_errors = [(yaml_file, errors)]
            all_errors.extend([(yaml_file, err) for err in errors])
            
            if verbose:
                typer.echo(f" ✗ ({len(errors)} error(s))")
                for err in errors:
                    typer.echo(f"    - {err}")
    
    typer.echo(f"\n{'='*60}")
    typer.echo(f"Validation Results:")
    typer.echo(f"  Valid: {valid_count}/{len(yaml_files)}")
    typer.echo(f"  Invalid: {invalid_count}/{len(yaml_files)}")
    typer.echo(f"  Total errors: {len(all_errors)}")
    
    if all_errors:
        typer.echo(f"\nErrors (showing up to {max_errors}):")
        for file_path, error in all_errors[:max_errors]:
            rel_path = file_path.relative_to(directory)
            typer.echo(f"  {rel_path}: {error}")
        
        if len(all_errors) > max_errors:
            typer.echo(f"\n  ... and {len(all_errors) - max_errors} more errors")
        
        # Group errors by type
        error_types = defaultdict(int)
        for _, error in all_errors:
            if "HTTP" in error:
                error_types["HTTP errors"] += 1
            elif "wikidata" in error.lower() or "Wikidata" in error:
                error_types["Wikidata errors"] += 1
            elif "URL" in error:
                error_types["URL format errors"] += 1
            else:
                error_types["Other errors"] += 1
        
        typer.echo(f"\nError summary by type:")
        for error_type, count in sorted(error_types.items()):
            typer.echo(f"  {error_type}: {count}")
        
        raise typer.Exit(1)
    else:
        typer.echo("\n✅ All files are valid!")
        return 0


if __name__ == "__main__":
    app()

