import json
import os
import sys
from unittest.mock import patch
import pytest

# Add the parent directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import main

def test_read_config_valid():
    """Test read_config with a valid config file."""
    config_data = {"name": "test_app", "version": "1.0"}
    with open("valid_config.json", "w") as f:
        json.dump(config_data, f)
    
    assert main.read_config("valid_config.json") == config_data
    os.remove("valid_config.json")

def test_read_config_missing_name():
    """Test read_config with a missing 'name' key."""
    config_data = {"version": "1.0"}
    with open("invalid_config.json", "w") as f:
        json.dump(config_data, f)
    
    with pytest.raises(ValueError) as excinfo:
        main.read_config("invalid_config.json")
    assert str(excinfo.value) == "Config must contain 'name' and 'version'."
    os.remove("invalid_config.json")

def test_read_config_missing_version():
    """Test read_config with a missing 'version' key."""
    config_data = {"name": "test_app"}
    with open("invalid_config.json", "w") as f:
        json.dump(config_data, f)
    
    with pytest.raises(ValueError) as excinfo:
        main.read_config("invalid_config.json")
    assert str(excinfo.value) == "Config must contain 'name' and 'version'."
    os.remove("invalid_config.json")

def test_read_config_invalid_json():
    """Test read_config with an invalid JSON file."""
    with open("invalid_config.json", "w") as f:
        f.write("{invalid json}")
    
    with pytest.raises(SystemExit) as excinfo:
        main.read_config("invalid_config.json")
    assert excinfo.type == SystemExit
    os.remove("invalid_config.json")

def test_read_config_nonexistent_file():
    """Test read_config with a nonexistent file."""
    with pytest.raises(SystemExit) as excinfo:
        main.read_config("nonexistent_config.json")
    assert excinfo.type == SystemExit

if __name__ == "__main__":
    pytest.main()
