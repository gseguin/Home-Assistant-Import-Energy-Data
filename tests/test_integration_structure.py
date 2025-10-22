"""Tests for the HACS integration structure."""

import json
import sys
from pathlib import Path


def test_manifest_json():
    """Test that manifest.json is valid."""
    manifest_path = Path(__file__).parent.parent / "custom_components" / "energy_data_importer" / "manifest.json"
    
    assert manifest_path.exists(), "manifest.json not found"
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    # Check required keys
    assert "domain" in manifest, "manifest.json missing 'domain'"
    assert "name" in manifest, "manifest.json missing 'name'"
    assert "documentation" in manifest, "manifest.json missing 'documentation'"
    assert "codeowners" in manifest, "manifest.json missing 'codeowners'"
    assert "version" in manifest, "manifest.json missing 'version'"
    assert "requirements" in manifest, "manifest.json missing 'requirements'"
    
    # Check values
    assert manifest["domain"] == "energy_data_importer"
    assert len(manifest["codeowners"]) > 0
    assert len(manifest["requirements"]) > 0


def test_hacs_json():
    """Test that hacs.json is valid."""
    hacs_path = Path(__file__).parent.parent / "hacs.json"
    
    assert hacs_path.exists(), "hacs.json not found"
    
    with open(hacs_path) as f:
        hacs_data = json.load(f)
    
    assert "name" in hacs_data, "hacs.json missing 'name'"


def test_required_files():
    """Test that all required files exist."""
    integration_path = Path(__file__).parent.parent / "custom_components" / "energy_data_importer"
    
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
        assert file_path.exists(), f"Required file not found: {filename}"


def test_translations():
    """Test that translations directory and files exist."""
    translations_path = Path(__file__).parent.parent / "custom_components" / "energy_data_importer" / "translations"
    
    assert translations_path.exists(), "translations directory not found"
    
    en_json = translations_path / "en.json"
    assert en_json.exists(), "en.json not found"
    
    with open(en_json) as f:
        translations = json.load(f)
    
    assert "config" in translations, "translations missing 'config' key"


def test_datasources_exist():
    """Test that datasources directory and key files exist."""
    datasources_path = Path(__file__).parent.parent / "Datasources"
    
    assert datasources_path.exists(), "Datasources directory not found"
    
    key_files = ["ImportData.py", "DataPrepareEngine.py"]
    for filename in key_files:
        file_path = datasources_path / filename
        assert file_path.exists(), f"Datasource file not found: {filename}"


def test_import_integration():
    """Test that the integration const module can be imported."""
    integration_path = Path(__file__).parent.parent / "custom_components"
    sys.path.insert(0, str(integration_path))
    
    try:
        # Try to import the const module (doesn't require Home Assistant)
        try:
            from energy_data_importer import const
        except ImportError as e:
            # If voluptuous or homeassistant is not installed, that's OK
            # This test is mainly to check the module structure
            if "voluptuous" in str(e) or "homeassistant" in str(e):
                print("  (Skipping import test - Home Assistant dependencies not installed)")
                return
            raise
        
        # Check that key constants are defined
        assert hasattr(const, "DOMAIN")
        assert hasattr(const, "SERVICE_PREPARE_DATA")
        assert hasattr(const, "SERVICE_IMPORT_DATA")
        assert hasattr(const, "DATA_SOURCES")
        
        # Check that data sources list is not empty
        assert len(const.DATA_SOURCES) > 0
        
    finally:
        if str(integration_path) in sys.path:
            sys.path.remove(str(integration_path))


if __name__ == "__main__":
    print("Running integration structure tests...")
    print()
    
    tests = [
        ("Manifest JSON", test_manifest_json),
        ("HACS JSON", test_hacs_json),
        ("Required Files", test_required_files),
        ("Translations", test_translations),
        ("Datasources", test_datasources_exist),
        ("Import Integration", test_import_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)

