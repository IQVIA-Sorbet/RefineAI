import ast

FORBIDDEN = (
    ast.Import, ast.ImportFrom,
    ast.Global, ast.With,
    ast.Try, ast.While
)

FORBIDDEN_CALLS = {"eval", "exec", "open", "__import__"}

def validate_code(code):
    """
    Checks for forbidden syntax and security-sensitive function calls.
    This is a simple, reliable check that should be kept.
    """
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, FORBIDDEN):
            raise ValueError(f"Forbidden AST node: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                raise ValueError(f"Forbidden call: {node.func.id}")
    return True

def sanitize_code(text: str) -> str:
    """Extracts a Python code block from an LLM response."""
    # ... (this function is fine, no changes needed) ...
    start_marker = text.find("```python")
    if start_marker == -1:
        start_marker = text.find("```")

    if start_marker != -1:
        end_marker = text.find("```", start_marker + 3)
        if end_marker != -1:
            return text[start_marker + (10 if "python" in text[start_marker:start_marker+10] else 3) : end_marker].strip()

    return text.strip()