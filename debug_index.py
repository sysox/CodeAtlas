from pathlib import Path
from codeatlas.py_symbols import list_python_symbols
from codeatlas.index import _kind_from_path

root = Path(".")
target_file = "src/codeatlas/cli.py"
full_path = root / target_file

print(f"Checking {target_file}...")
print(f"Kind: {_kind_from_path(target_file)}")

if full_path.exists():
    try:
        symbols = list_python_symbols(full_path)
        print(f"Found {len(symbols)} symbols:")
        for s in symbols:
            print(f"  - {s['qualname']} ({s['kind']})")
    except Exception as e:
        print(f"Error parsing symbols: {e}")
else:
    print("File not found.")
