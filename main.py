import json
import sys

def read_config(file_path):
    """Read and validate JSON config file."""
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        
        if "name" not in config or "version" not in config:
            raise ValueError("Config must contain 'name' and 'version'.")
        
        return config
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)
    
    config = read_config(sys.argv[1])
    print(f"Config loaded successfully. Name: {config['name']}, Version: {config['version']}")
