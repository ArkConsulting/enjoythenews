import json
import sys

def read_config(file_path):
    """Read and validate JSON config file."""
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        
        if "name" not in config or "version" not in config:
            raise ValueError(f"Config must contain 'name' and 'version'. File: {file_path}")
        
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"The file {file_path} is not a valid JSON. Error: {e}", e.doc, e.pos)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file>")
        sys.exit(1)
    
    config = read_config(sys.argv[1])
    print(f"Config loaded successfully. Name: {config['name']}, Version: {config['version']}")

if __name__ == "__main__":
    main()
