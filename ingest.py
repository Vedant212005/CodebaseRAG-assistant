import ast
import os
import json

# ---------- Helper functions ----------

def get_names_from_calls(node):
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.append(child.func.attr)
    return list(set(calls))


def get_variable_names(node):
    return list({n.id for n in ast.walk(node) if isinstance(n, ast.Name)})


def get_constants(node):
    consts = set()
    for c in ast.walk(node):
        if isinstance(c, ast.Constant) and isinstance(c.value, (str, int, float)):
            consts.add(c.value)
    return list(consts)

# ---------- Core parser ----------

def parse_python_file(file_path):
    """Parse one .py file into chunks."""
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

            parent_class = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef) and node in parent.body:
                    parent_class = parent.name
                    break

            kind = "method" if parent_class else "function"
            snippet = code[:250].replace('\n', ' ')

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
def run_ingest(repo_path: str, out_file: str):
    """
    Parse all Python files in repo_path and write chunks to out_file.
    This is session-safe and backend-callable.
    """
    all_chunks = []

    if os.path.isdir(repo_path):
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    fpath = os.path.join(root, file)
                    all_chunks.extend(parse_python_file(fpath))
    else:
        all_chunks.extend(parse_python_file(repo_path))

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)


