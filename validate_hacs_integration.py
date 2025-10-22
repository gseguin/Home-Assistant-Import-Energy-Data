#!/usr/bin/env python3
"""Validate the HACS integration structure."""

import json
import sys
from pathlib import Path


def validate_manifest(manifest_path: Path) -> list[str]:
    """Validate manifest.json."""
    errors = []
    
    if not manifest_path.exists():
        errors.append("manifest.json not found")
        return errors
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        required_keys = ["domain", "name", "documentation", "codeowners", "version"]
        for key in required_keys:
            if key not in manifest:
                errors.append(f"manifest.json missing required key: {key}")
        
        if "requirements" not in manifest:
            errors.append("manifest.json missing requirements")
        
        print(f"✓ manifest.json is valid")
        print(f"  - Domain: {manifest.get('domain')}")
        print(f"  - Name: {manifest.get('name')}")
        print(f"  - Version: {manifest.get('version')}")
        
    except json.JSONDecodeError as e:
        errors.append(f"manifest.json is not valid JSON: {e}")
    
    return errors


def validate_hacs_json(hacs_json_path: Path) -> list[str]:
    """Validate hacs.json."""
    errors = []
    
    if not hacs_json_path.exists():
        errors.append("hacs.json not found")
        return errors
    
    try:
        with open(hacs_json_path) as f:
            hacs_data = json.load(f)
        
        if "name" not in hacs_data:
            errors.append("hacs.json missing 'name' key")
        
        print(f"✓ hacs.json is valid")
        print(f"  - Name: {hacs_data.get('name')}")
        
    except json.JSONDecodeError as e:
        errors.append(f"hacs.json is not valid JSON: {e}")
    
    return errors


def validate_file_structure(integration_path: Path) -> list[str]:
    """Validate the file structure."""
    errors = []
    
    required_files = [
        "__init__.py",
        "manifest.json",
        "const.py",
        "config_flow.py",
        "services.yaml",
        "strings.json",
    ]
    
    for filename in required_files:
        file_path = integration_path / filename
        if not file_path.exists():
            errors.append(f"Missing required file: {filename}")
        else:
            print(f"✓ Found {filename}")
    
    # Check for translations
    translations_path = integration_path / "translations"
    if not translations_path.exists():
        errors.append("Missing translations directory")
    else:
        en_json = translations_path / "en.json"
        if not en_json.exists():
            errors.append("Missing translations/en.json")
        else:
            print(f"✓ Found translations/en.json")
    
    return errors


def validate_datasources(repo_root: Path) -> list[str]:
    """Validate datasources are available."""
    errors = []
    
    datasources_path = repo_root / "Datasources"
    if not datasources_path.exists():
        errors.append("Datasources directory not found")
        return errors
    
    # Check for key files
    key_files = ["ImportData.py", "DataPrepareEngine.py"]
    for filename in key_files:
        file_path = datasources_path / filename
        if not file_path.exists():
            errors.append(f"Missing datasources file: {filename}")
        else:
            print(f"✓ Found Datasources/{filename}")
    
    return errors


def main():
    """Main validation function."""
    print("=" * 60)
    print("HACS Integration Validation")
    print("=" * 60)
    print()
    
    repo_root = Path(__file__).parent
    integration_path = repo_root / "custom_components" / "energy_data_importer"
    hacs_json_path = repo_root / "hacs.json"
    
    all_errors = []
    
    print("Checking file structure...")
    all_errors.extend(validate_file_structure(integration_path))
    print()
    
    print("Validating manifest.json...")
    all_errors.extend(validate_manifest(integration_path / "manifest.json"))
    print()
    
    print("Validating hacs.json...")
    all_errors.extend(validate_hacs_json(hacs_json_path))
    print()
    
    print("Validating datasources...")
    all_errors.extend(validate_datasources(repo_root))
    print()
    
    print("=" * 60)
    if all_errors:
        print("❌ Validation failed with the following errors:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ All validations passed!")
        print()
        print("Next steps:")
        print("  1. Test locally using the guide in HACS_INSTALLATION.md")
        print("  2. Create a PR to the original repository")
        print("  3. Wait for HACS validation to pass")
    print("=" * 60)


if __name__ == "__main__":
    main()

