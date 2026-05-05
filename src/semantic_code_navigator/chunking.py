from __future__ import annotations

import ast

from semantic_code_navigator.models import CodeChunk, SourceFile


def chunk_python_file(source_file: SourceFile, max_lines: int = 80) -> list[CodeChunk]:
    lines = source_file.content.splitlines()
    chunks: list[CodeChunk] = []

    try:
        tree = ast.parse(source_file.content)
    except SyntaxError:
        return _line_chunks(source_file.relative_path, lines, max_lines)

    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        and hasattr(node, "lineno")
        and hasattr(node, "end_lineno")
    ]

    import_block = _collect_import_block(lines)
    module_docstring = _module_docstring(tree)

    for node in nodes:
        end_lineno = node.end_lineno or node.lineno
        node_body = "\n".join(lines[node.lineno - 1 : end_lineno])
        header_parts = [import_block, module_docstring, _node_docstring(node)]
        header = "\n".join(part for part in header_parts if part).strip()
        content = f"{header}\n\n{node_body}" if header else node_body
        chunks.append(
            CodeChunk(
                file_path=source_file.relative_path,
                start_line=node.lineno,
                end_line=end_lineno,
                content=content,
                symbol=node.name,
            )
        )

    covered = {(chunk.start_line, chunk.end_line) for chunk in chunks}
    module_lines = _uncovered_lines(lines, covered)
    if module_lines.strip():
        chunks.insert(
            0,
            CodeChunk(
                file_path=source_file.relative_path,
                start_line=1,
                end_line=len(lines),
                content=module_lines,
                symbol=None,
            ),
        )

    return chunks or _line_chunks(source_file.relative_path, lines, max_lines)


def _collect_import_block(lines: list[str]) -> str:
    imports: list[str] = []
    for line in lines[:60]:
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(line)
    return "\n".join(imports)


def _module_docstring(tree: ast.AST) -> str:
    value = ast.get_docstring(tree, clean=False)
    if not value:
        return ""
    return f'"""{value}"""'


def _node_docstring(node: ast.AST) -> str:
    value = ast.get_docstring(node, clean=False)
    if not value:
        return ""
    return f'"""{value}"""'


def _uncovered_lines(lines: list[str], ranges: set[tuple[int, int]]) -> str:
    output: list[str] = []
    for line_no, line in enumerate(lines, start=1):
        if any(start <= line_no <= end for start, end in ranges):
            continue
        if line.strip():
            output.append(line)
    return "\n".join(output)


def _line_chunks(file_path: str, lines: list[str], max_lines: int) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []
    for start in range(0, len(lines), max_lines):
        end = min(start + max_lines, len(lines))
        content = "\n".join(lines[start:end])
        if content.strip():
            chunks.append(
                CodeChunk(
                    file_path=file_path,
                    start_line=start + 1,
                    end_line=end,
                    content=content,
                    symbol=None,
                )
            )
    return chunks
