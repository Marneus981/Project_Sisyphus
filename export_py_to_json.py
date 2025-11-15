import json
import importlib.util
import sys
import os

def clean(obj):
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items() if not callable(v) and not hasattr(v, '__module__')}
    elif isinstance(obj, list):
        return [clean(i) for i in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"config", "debug", "payloads"}:
        print("Usage: python export_py_to_json.py [config|debug|payloads]")
        sys.exit(1)

    arg = sys.argv[1]
    base_dir = os.path.dirname(__file__)
    py_dir = os.path.join(base_dir, 'settings', 'editable_py')
    json_dir = os.path.join(base_dir, 'settings', 'json')

    if arg == "config":
        py_file = os.path.join(py_dir, 'settings.py')
        var_name = 'CONFIG'
        json_file = os.path.join(json_dir, 'settings.json')
    elif arg == "debug":
        py_file = os.path.join(py_dir, 'debug.py')
        var_name = 'DEBUG'
        json_file = os.path.join(json_dir, 'debug.json')
    elif arg == "payloads":
        py_file = os.path.join(py_dir, 'payloads.py')
        var_name = 'PAYLOADS'
        json_file = os.path.join(json_dir, 'payloads.json')

    # Dynamically import the module
    spec = importlib.util.spec_from_file_location(arg, py_file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[arg] = mod
    spec.loader.exec_module(mod)

    # Get the dictionary
    data = getattr(mod, var_name)
    data_clean = clean(data)

    # Write to the appropriate JSON file
    os.makedirs(json_dir, exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data_clean, f, ensure_ascii=False, indent=2)

    print(f'{var_name} exported to {json_file}')

if __name__ == "__main__":
    main()
