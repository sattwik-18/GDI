#!/usr/bin/env python3
"""Clean Architecture Boundary Enforcer.

Statically analyzes all Python modules in `src/domain/` to guarantee that domain entities,
interfaces, and exceptions remain 100% pure Python and do not import any external framework
or infrastructure dependencies (FastAPI, SQLAlchemy, OpenCV, PaddleOCR, PyMuPDF, etc.).
"""

import ast
import os
import sys

PROHIBITED_DOMAIN_IMPORTS = {
    "fastapi",
    "starlette",
    "sqlalchemy",
    "asyncpg",
    "cv2",
    "paddle",
    "paddleocr",
    "fitz",
    "pytesseract",
    "httpx",
    "src.infrastructure",
    "src.api",
}


def check_file_imports(filepath: str) -> list[str]:
    """Inspects a Python file AST for prohibited framework imports."""
    violations: list[str] = []
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    for node in ast.walk(tree):
        # Ignore TYPE_CHECKING blocks
        if isinstance(node, ast.If):
            if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                continue

        if isinstance(node, ast.Import):
            for alias in node.names:
                for prohibited in PROHIBITED_DOMAIN_IMPORTS:
                    if alias.name == prohibited or alias.name.startswith(prohibited + "."):
                        violations.append(
                            f"{filepath}:{node.lineno} -- Prohibited import '{alias.name}'"
                        )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for prohibited in PROHIBITED_DOMAIN_IMPORTS:
                    if node.module == prohibited or node.module.startswith(prohibited + "."):
                        violations.append(
                            f"{filepath}:{node.lineno} -- Prohibited import from '{node.module}'"
                        )

    return violations


def validate_clean_architecture() -> int:
    """Scans src/domain/ directory for architecture boundary violations."""
    domain_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "domain")
    all_violations: list[str] = []

    print("==================================================")
    print("--- CLEAN ARCHITECTURE BOUNDARY CHECK ---")
    print(f"Scanning domain directory: {domain_dir}")

    for root, _, files in os.walk(domain_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                violations = check_file_imports(filepath)
                all_violations.extend(violations)

    if all_violations:
        print(f"[FAIL] Clean Architecture Violations Found ({len(all_violations)}):")
        for v in all_violations:
            print(f"   {v}")
        return 1

    print("[OK] CLEAN ARCHITECTURE CHECK PASSED! Zero domain layer boundary violations.")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(validate_clean_architecture())
