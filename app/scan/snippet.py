import os

def get_code_snippet(file_path: str, line_number: int, context_lines: int = 3):
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        snippet_lines = []
        for i in range(start, end):
            prefix = ">" if i == line_number - 1 else " "
            snippet_lines.append(f"{prefix} {i+1:4d} {lines[i].rstrip()}")
        return {
            "snippet": "\n".join(snippet_lines),
            "line": line_number,
            "file": file_path
        }
    except Exception as e:
        return {"error": str(e)}