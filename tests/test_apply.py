import json
from pathlib import Path
from codeatlas.apply import apply_change_packet

def test_apply_replace_symbol(tmp_path: Path):
    # Setup: Create a file with a class and a function
    file_path = tmp_path / "test_code.py"
    original_code = """
class MyClass:
    def method(self):
        return "original method"

def my_function():
    return "original function"
""".lstrip()
    file_path.write_text(original_code, encoding="utf-8")

    # Create a change packet to replace 'my_function'
    new_function_code = """def my_function():
    return "new function"
"""
    packet = [
        {
            "op": "replace_symbol",
            "path": "test_code.py",
            "qualname": "my_function",
            "new_code": new_function_code
        }
    ]
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    # Execute apply
    result = apply_change_packet(tmp_path, packet_path)

    # Assertions
    assert result["ok"] is True
    assert result["results"][0]["status"] == "symbol_replaced_cst"

    # Verify file content
    new_content = file_path.read_text(encoding="utf-8")
    
    # The class should be untouched
    assert "class MyClass:" in new_content
    assert 'return "original method"' in new_content
    
    # The function should be replaced
    assert 'return "new function"' in new_content
    assert 'return "original function"' not in new_content

def test_apply_replace_nested_symbol(tmp_path: Path):
    # Setup: Create a file with a class and a method
    file_path = tmp_path / "test_nested.py"
    original_code = """
class A:
    def m(self):
        return 1
""".lstrip()
    file_path.write_text(original_code, encoding="utf-8")

    # Create a change packet to replace 'A.m'
    new_method_code = """    def m(self):
        return 2
"""
    packet = [
        {
            "op": "replace_symbol",
            "path": "test_nested.py",
            "qualname": "A.m",
            "new_code": new_method_code
        }
    ]
    packet_path = tmp_path / "packet_nested.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    # Execute apply
    result = apply_change_packet(tmp_path, packet_path)

    # Assertions
    assert result["ok"] is True
    
    # Verify file content
    new_content = file_path.read_text(encoding="utf-8")
    assert "return 2" in new_content
    assert "return 1" not in new_content

def test_apply_multiple_replacements(tmp_path: Path):
    # Setup: Create a file with two functions
    file_path = tmp_path / "test_multi.py"
    original_code = """
def foo():
    return 1

def bar():
    return 2
""".lstrip()
    file_path.write_text(original_code, encoding="utf-8")

    # Create a change packet to replace BOTH functions
    packet = [
        {
            "op": "replace_symbol",
            "path": "test_multi.py",
            "qualname": "foo",
            "new_code": "def foo():\n    return 10\n"
        },
        {
            "op": "replace_symbol",
            "path": "test_multi.py",
            "qualname": "bar",
            "new_code": "def bar():\n    return 20\n"
        }
    ]
    packet_path = tmp_path / "packet_multi.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    # Execute apply
    result = apply_change_packet(tmp_path, packet_path)

    # Assertions
    assert result["ok"] is True
    assert len(result["results"]) == 2
    
    # Verify file content
    new_content = file_path.read_text(encoding="utf-8")
    assert "return 10" in new_content
    assert "return 20" in new_content
