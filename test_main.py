import json
import os
import sys
from unittest.mock import patch
import pytest

# Add the parent directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import main

import tempfile

def test_read_config_valid():
    """Test read_config with a valid config file."""
    config_data = {"name": "test_app", "version": "1.0"}
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        json.dump(config_data, f)
        temp_file_path = f.name
    
    assert main.read_config(temp_file_path) == config_data
    os.remove(temp_file_path)

def test_read_config_missing_name():
    """Test read_config with a missing 'name' key."""
    config_data = {"version": "1.0"}
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        json.dump(config_data, f)
        temp_file_path = f.name
    
    with pytest.raises(ValueError) as excinfo:
        main.read_config(temp_file_path)
    assert str(excinfo.value).startswith("Config must contain 'name' and 'version'. File:")
    os.remove(temp_file_path)

def test_read_config_missing_version():
    """Test read_config with a missing 'version' key."""
    config_data = {"name": "test_app"}
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        json.dump(config_data, f)
        temp_file_path = f.name
    
    with pytest.raises(ValueError) as excinfo:
        main.read_config(temp_file_path)
    assert str(excinfo.value).startswith("Config must contain 'name' and 'version'. File:")
    os.remove(temp_file_path)

def test_read_config_invalid_json():
    """Test read_config with an invalid JSON file."""
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write("{invalid json}")
        temp_file_path = f.name
    
    with pytest.raises(json.JSONDecodeError) as excinfo:
        main.read_config(temp_file_path)
    assert str(excinfo.value).startswith("The file")
    os.remove(temp_file_path)

def test_read_config_nonexistent_file():
    """Test read_config with a nonexistent file."""
    with pytest.raises(FileNotFoundError) as excinfo:
        main.read_config("nonexistent_config.json")
    assert str(excinfo.value).startswith("The file")

if __name__ == "__main__":
    pytest.main()
