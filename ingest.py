import ast
import os
import json

# ---------- Helper functions ----------

def get_names_from_calls(node):
    """
    Extract names of all functions called inside this node.
    Example: connect_to_db(), send_email() → ['connect_to_db', 'send_email']
    """
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.append(child.func.attr)
    return list(set(calls))


def get_variable_names(node):
    """
    Extract variable identifiers used or defined in the function.
    Example: balance, amount, conn
    """
    return list({n.id for n in ast.walk(node) if isinstance(n, ast.Name)})


def get_constants(node):
    """
    Extract literal constants (strings / ints / floats) appearing in code.
    Example: 'Payment successful', 500
    """
    consts = set()
    for c in ast.walk(node):
        if isinstance(c, ast.Constant) and isinstance(c.value, (str, int, float)):
            consts.add(c.value)
    return list(consts)

# ---------- Core parser ----------

def parse_python_file(file_path):
    """Parse one .py file → list of structured code chunks (functions, classes)."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    results = []

    for node in ast.walk(tree):

        # ----- FUNCTIONS & ASYNC FUNCTIONS -----
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start, end = getattr(node, "lineno", 0), getattr(node, "end_lineno", 0)
            doc = ast.get_docstring(node)
            code = ast.get_source_segment(source, node) or ""
            args = [a.arg for a in node.args.args]
            calls = get_names_from_calls(node)
            vars_ = get_variable_names(node)
            consts = get_constants(node)

            # check if method (inside class)
            parent_class = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef) and node in parent.body:
                    parent_class = parent.name
                    break

            kind = "method" if parent_class else "function"

            # Fix: handle newline replacement *outside* f-string
            snippet = code[:250].replace('\n', ' ')

            # -------- Build text for embeddings --------
            text_to_embed = f"""
            {kind.title()}: {node.name}
            Class: {parent_class or 'None'}
            Arguments: {', '.join(args) or 'None'}
            Docstring: {doc or 'None'}
            Calls: {', '.join(calls) or 'None'}
            Variables: {', '.join(vars_) or 'None'}
            Constants: {', '.join(map(str, consts)) or 'None'}
            Code sample: {snippet}
            """

            results.append({
                "kind": kind,
                "name": node.name,
                "class": parent_class,
                "file": os.path.basename(file_path),
                "lineno_start": start,
                "lineno_end": end,
                "docstring": doc,
                "args": args,
                "calls": calls,
                "variables": vars_,
                "constants": consts,
                "code": code,
                "text_to_embed": text_to_embed.strip()
            })

        # ----- CLASSES -----
        elif isinstance(node, ast.ClassDef):
            start, end = getattr(node, "lineno", 0), getattr(node, "end_lineno", 0)
            doc = ast.get_docstring(node)
            code = ast.get_source_segment(source, node) or ""

            # Fix: handle newline replacement outside f-string
            snippet = code[:250].replace('\n', ' ')

            text_to_embed = f"""
            Class: {node.name}
            Docstring: {doc or 'None'}
            Code sample: {snippet}
            """

            results.append({
                "kind": "class",
                "name": node.name,
                "file": os.path.basename(file_path),
                "lineno_start": start,
                "lineno_end": end,
                "docstring": doc,
                "code": code,
                "text_to_embed": text_to_embed.strip()
            })

    return results

# ---------- Runner (single file or folder) ----------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse Python codebase into structured code chunks.")
    parser.add_argument("path", nargs="?", default=".", help="Path to a Python file or directory (default: current folder)")
    parser.add_argument("--out", default="code_chunks.json", help="Output JSON file (default: code_chunks.json)")
    args = parser.parse_args()

    all_chunks = []

    # Handle both single file and directory
    if os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for file in files:
                if file.endswith(".py"):
                    fpath = os.path.join(root, file)
                    print(f"🔍 Parsing {fpath} ...")
                    all_chunks.extend(parse_python_file(fpath))
    else:
        all_chunks.extend(parse_python_file(args.path))

    # Save results to JSON
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Extracted {len(all_chunks)} code chunks.")
    print(f"📁 Saved output → {args.out}")
