#!/usr/bin/env python3
"""
DevOps-OS Unit Test Scaffold Generator

Generates unit testing configuration and sample test files for multiple
tech stacks:

  Python   : pytest + pytest-cov (pytest.ini, conftest.py, sample test)
  JavaScript/TypeScript:
    jest    : jest.config.js + sample test
    mocha   : .mocharc.js + sample test
    vitest  : vitest.config.js + sample test
  Go       : go test convention (Makefile snippet + sample *_test.go)

Output layout (default: <output-dir>/ in the current directory):
  <output-dir>/
  ├── pytest.ini              # Python — pytest configuration
  ├── conftest.py             # Python — shared fixtures
  ├── tests/__init__.py       # Python — test-package marker
  ├── tests/test_sample.py    # Python — sample unit tests
  ├── jest.config.js          # JS/TS (jest) — Jest configuration
  ├── vitest.config.js        # JS/TS (vitest) — Vitest configuration
  ├── .mocharc.js             # JS/TS (mocha) — Mocha configuration
  ├── tests/sample.test.js    # JS/TS — sample unit tests
  ├── Makefile.test           # Go — test Makefile targets
  └── sample_test.go          # Go — sample unit test file
"""

import os
import sys
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENV_PREFIX = "DEVOPS_OS_UNITTEST_"

SUPPORTED_LANGUAGES = ["python", "javascript", "typescript", "go"]
JS_FRAMEWORKS = ["jest", "mocha", "vitest"]
FRAMEWORK_DEFAULTS = {
    "python": "pytest",
    "javascript": "jest",
    "typescript": "jest",
    "go": "go-test",
}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_arguments():
    """Parse command-line arguments with environment variable fallbacks."""
    parser = argparse.ArgumentParser(
        description="Generate unit testing configuration and sample test files for DevOps-OS"
    )
    parser.add_argument(
        "--name",
        default=os.environ.get(f"{ENV_PREFIX}NAME", "my-app"),
        help="Project / application name (used in generated file content)",
    )
    parser.add_argument(
        "--languages",
        default=os.environ.get(f"{ENV_PREFIX}LANGUAGES", "python"),
        help=(
            "Comma-separated list of languages to generate tests for: "
            "python, javascript, typescript, go"
        ),
    )
    parser.add_argument(
        "--framework",
        default=os.environ.get(f"{ENV_PREFIX}FRAMEWORK", ""),
        help=(
            "Testing framework override (auto-selected per language by default). "
            "For JavaScript/TypeScript: jest | mocha | vitest. "
            "For Python: pytest. For Go: go-test."
        ),
    )
    parser.add_argument(
        "--coverage",
        dest="coverage",
        action="store_true",
        default=os.environ.get(f"{ENV_PREFIX}COVERAGE", "true").lower()
        in ("true", "1", "yes"),
        help="Include coverage configuration (default: true)",
    )
    parser.add_argument(
        "--no-coverage",
        dest="coverage",
        action="store_false",
        help="Disable coverage configuration",
    )
    parser.add_argument(
        "--output-dir",
        default=os.environ.get(f"{ENV_PREFIX}OUTPUT_DIR", "unittest"),
        help="Root output directory for generated files (default: unittest/)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# File-writing helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    """Write *content* to *path*, creating intermediate directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Python / pytest generators
# ---------------------------------------------------------------------------

def generate_pytest_ini(name: str, coverage: bool) -> str:
    """Return the content of a pytest.ini file."""
    cov_opts = (
        f"\naddopts =\n"
        f"    --cov={name.replace('-', '_')}\n"
        f"    --cov-report=term-missing\n"
        f"    --cov-report=xml:coverage.xml\n"
        f"    --cov-report=html:htmlcov\n"
    ) if coverage else ""
    return (
        "[pytest]\n"
        f"# pytest configuration for {name}\n"
        "testpaths = tests\n"
        "python_files = test_*.py *_test.py\n"
        "python_classes = Test*\n"
        "python_functions = test_*\n"
        f"{cov_opts}"
    )


def generate_conftest_py(name: str) -> str:
    """Return the content of a conftest.py file with sample fixtures."""
    module = name.replace("-", "_")
    return (
        f'"""Shared pytest fixtures for {name}."""\n'
        "\n"
        "import pytest\n"
        "\n"
        "\n"
        "@pytest.fixture\n"
        "def sample_config():\n"
        '    """Return a minimal application configuration dict."""\n'
        "    return {\n"
        f'        "name": "{name}",\n'
        '        "version": "0.1.0",\n'
        '        "debug": False,\n'
        "    }\n"
        "\n"
        "\n"
        "@pytest.fixture\n"
        f"def {module}_client(sample_config):\n"
        f'    """Return a lightweight {name} client stub."""\n'
        "    class _Stub:\n"
        "        def __init__(self, cfg):\n"
        "            self.config = cfg\n"
        "\n"
        "        def ping(self):\n"
        "            return True\n"
        "\n"
        f"    return _Stub(sample_config)\n"
    )


def generate_python_test_sample(name: str) -> str:
    """Return a sample Python unit test file."""
    module = name.replace("-", "_")
    return (
        f'"""Sample unit tests for {name}.\n'
        "\n"
        "Replace these stubs with real tests for your application logic.\n"
        '"""\n'
        "\n"
        "import pytest\n"
        "\n"
        "\n"
        f"class Test{module.title().replace('_', '')}Core:\n"
        f'    """Core unit tests for {name}."""\n'
        "\n"
        "    def test_addition(self):\n"
        '        """Trivial sanity check — always passes."""\n'
        "        assert 1 + 1 == 2\n"
        "\n"
        "    def test_string_format(self):\n"
        '        """Verify basic string formatting."""\n'
        f'        result = f"Hello from {name}"\n'
        f'        assert "Hello" in result\n'
        "\n"
        "    def test_list_operations(self):\n"
        '        """Verify list membership."""\n'
        "        items = [1, 2, 3, 4, 5]\n"
        "        assert 3 in items\n"
        "        assert len(items) == 5\n"
        "\n"
        "\n"
        "class TestEdgeCases:\n"
        '    """Edge-case tests."""\n'
        "\n"
        "    def test_empty_string(self):\n"
        "        assert len(\"\") == 0\n"
        "\n"
        "    def test_none_check(self):\n"
        "        value = None\n"
        "        assert value is None\n"
        "\n"
        "    @pytest.mark.parametrize(\n"
        "        \"a, b, expected\",\n"
        "        [\n"
        "            (1, 2, 3),\n"
        "            (0, 0, 0),\n"
        "            (-1, 1, 0),\n"
        "        ],\n"
        "    )\n"
        "    def test_parametrized_add(self, a, b, expected):\n"
        "        assert a + b == expected\n"
        "\n"
        "\n"
        "def test_fixture_ping(sample_config):\n"
        f'    """Verify the sample_config fixture is populated."""\n'
        f'    assert sample_config["name"] == "{name}"\n'
    )


def generate_python_tests_init() -> str:
    return '"""Test package for unit tests."""\n'


# ---------------------------------------------------------------------------
# JavaScript / TypeScript generators
# ---------------------------------------------------------------------------

def generate_jest_config(name: str, is_typescript: bool, coverage: bool) -> str:
    """Return the content of a jest.config.js file."""
    transform = (
        "  transform: {\n"
        "    '^.+\\\\.(ts|tsx)$': 'ts-jest',\n"
        "  },\n"
        "  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],\n"
    ) if is_typescript else ""

    cov_block = ""
    if coverage:
        cov_block = (
            "  collectCoverage: true,\n"
            "  coverageDirectory: 'coverage',\n"
            "  coverageReporters: ['text', 'lcov', 'html'],\n"
            "  collectCoverageFrom: [\n"
            "    'src/**/*.{js,ts}',\n"
            "    '!src/**/*.d.ts',\n"
            "    '!src/index.{js,ts}',\n"
            "  ],\n"
            "  coverageThreshold: {\n"
            "    global: {\n"
            "      branches: 70,\n"
            "      functions: 70,\n"
            "      lines: 70,\n"
            "      statements: 70,\n"
            "    },\n"
            "  },\n"
        )

    return (
        f"// Jest configuration for {name}\n"
        "/** @type {import('jest').Config} */\n"
        "module.exports = {\n"
        "  testEnvironment: 'node',\n"
        "  testMatch: [\n"
        "    '**/__tests__/**/*.[jt]s?(x)',\n"
        "    '**/?(*.)+(spec|test).[jt]s?(x)',\n"
        "  ],\n"
        f"{transform}"
        f"{cov_block}"
        "  verbose: true,\n"
        "  clearMocks: true,\n"
        "};\n"
    )


def generate_vitest_config(name: str, coverage: bool) -> str:
    """Return the content of a vitest.config.js file."""
    cov_block = ""
    if coverage:
        cov_block = (
            "      coverage: {\n"
            "        provider: 'v8',\n"
            "        reporter: ['text', 'lcov', 'html'],\n"
            "        include: ['src/**/*.{js,ts}'],\n"
            "        exclude: ['src/**/*.d.ts', 'node_modules'],\n"
            "        thresholds: { lines: 70, functions: 70, branches: 70, statements: 70 },\n"
            "      },\n"
        )

    return (
        f"// Vitest configuration for {name}\n"
        "import { defineConfig } from 'vitest/config';\n"
        "\n"
        "export default defineConfig({\n"
        "  test: {\n"
        "    environment: 'node',\n"
        "    include: ['**/*.{test,spec}.{js,ts}'],\n"
        "    globals: true,\n"
        f"{cov_block}"
        "  },\n"
        "});\n"
    )


def generate_mocha_rc(name: str, coverage: bool) -> str:
    """Return the content of a .mocharc.js file."""
    nyc_comment = (
        "// Run with: nyc mocha  (install nyc for coverage)\n" if coverage else ""
    )
    return (
        f"// Mocha configuration for {name}\n"
        f"{nyc_comment}"
        "module.exports = {\n"
        "  spec: 'tests/**/*.test.{js,mjs}',\n"
        "  timeout: 5000,\n"
        "  reporter: 'spec',\n"
        "  recursive: true,\n"
        "};\n"
    )


def generate_js_test_sample(name: str, framework: str, is_typescript: bool) -> str:
    """Return a sample JavaScript/TypeScript unit test file."""
    ext = "ts" if is_typescript else "js"
    import_style = (
        "import { describe, it, expect, beforeEach } from 'vitest';"
        if framework == "vitest"
        else (
            "const { expect } = require('chai');"
            if framework == "mocha"
            else "// Jest globals are injected automatically"
        )
    )

    if framework == "mocha":
        return (
            f"// Sample Mocha + Chai unit tests for {name}\n"
            f"{import_style}\n"
            "\n"
            f"describe('{name} core', () => {{\n"
            "  it('should perform basic arithmetic', () => {\n"
            "    expect(1 + 1).to.equal(2);\n"
            "  });\n"
            "\n"
            "  it('should handle string operations', () => {\n"
            f"    const result = `Hello from {name}`;\n"
            "    expect(result).to.include('Hello');\n"
            "  });\n"
            "\n"
            "  it('should work with arrays', () => {\n"
            "    const items = [1, 2, 3];\n"
            "    expect(items).to.have.lengthOf(3);\n"
            "    expect(items).to.include(2);\n"
            "  });\n"
            "});\n"
            "\n"
            f"describe('{name} edge cases', () => {{\n"
            "  it('should handle empty values', () => {\n"
            "    expect('').to.equal('');\n"
            "    expect(null).to.be.null;\n"
            "  });\n"
            "});\n"
        )

    # jest / vitest share the same expect API
    return (
        f"// Sample {framework.capitalize()} unit tests for {name}\n"
        f"{import_style}\n"
        "\n"
        f"describe('{name} core', () => {{\n"
        "  it('should perform basic arithmetic', () => {\n"
        "    expect(1 + 1).toBe(2);\n"
        "  });\n"
        "\n"
        "  it('should handle string operations', () => {\n"
        f"    const result = `Hello from {name}`;\n"
        "    expect(result).toContain('Hello');\n"
        "  });\n"
        "\n"
        "  it('should work with arrays', () => {\n"
        "    const items = [1, 2, 3];\n"
        "    expect(items).toHaveLength(3);\n"
        "    expect(items).toContain(2);\n"
        "  });\n"
        "});\n"
        "\n"
        f"describe('{name} edge cases', () => {{\n"
        "  it('should handle null and undefined', () => {\n"
        "    expect(null).toBeNull();\n"
        "    expect(undefined).toBeUndefined();\n"
        "  });\n"
        "\n"
        "  it.each([\n"
        "    [1, 2, 3],\n"
        "    [0, 0, 0],\n"
        "    [-1, 1, 0],\n"
        "  ])('adds %i + %i to equal %i', (a, b, expected) => {\n"
        "    expect(a + b).toBe(expected);\n"
        "  });\n"
        "});\n"
    )


# ---------------------------------------------------------------------------
# Go generators
# ---------------------------------------------------------------------------

def generate_go_test_sample(name: str) -> str:
    """Return a sample Go unit test file."""
    pkg = name.replace("-", "_").lower()
    return (
        f"// Package {pkg} provides unit tests for {name}.\n"
        f"package {pkg}_test\n"
        "\n"
        'import (\n'
        '\t"testing"\n'
        ")\n"
        "\n"
        f"// TestAdd verifies basic arithmetic — replace with real application tests.\n"
        "func TestAdd(t *testing.T) {\n"
        "\tresult := 1 + 1\n"
        "\tif result != 2 {\n"
        '\t\tt.Errorf("expected 2, got %d", result)\n'
        "\t}\n"
        "}\n"
        "\n"
        "func TestStringContains(t *testing.T) {\n"
        f'\tgreeting := "Hello from {name}"\n'
        '\tif len(greeting) == 0 {\n'
        '\t\tt.Error("expected non-empty greeting")\n'
        "\t}\n"
        "}\n"
        "\n"
        "func TestTableDriven(t *testing.T) {\n"
        "\tcases := []struct {\n"
        "\t\ta, b, want int\n"
        "\t}{\n"
        "\t\t{1, 2, 3},\n"
        "\t\t{0, 0, 0},\n"
        "\t\t{-1, 1, 0},\n"
        "\t}\n"
        "\tfor _, tc := range cases {\n"
        "\t\tgot := tc.a + tc.b\n"
        "\t\tif got != tc.want {\n"
        '\t\t\tt.Errorf("add(%d, %d) = %d; want %d", tc.a, tc.b, got, tc.want)\n'
        "\t\t}\n"
        "\t}\n"
        "}\n"
    )


def generate_go_makefile(name: str, coverage: bool) -> str:
    """Return Makefile test-target content for a Go project."""
    pkg = name.replace("-", "_").lower()
    cov_target = ""
    if coverage:
        cov_target = (
            "\n"
            "# Generate HTML coverage report\n"
            "test-coverage: test\n"
            f"\tgo tool cover -html=coverage_{pkg}.out -o coverage_{pkg}.html\n"
            f"\t@echo \"Coverage report: coverage_{pkg}.html\"\n"
        )

    return (
        f"# Makefile test targets for {name}\n"
        "# Include these targets in your project Makefile\n"
        "\n"
        ".PHONY: test test-verbose test-race lint\n"
        "\n"
        "# Run all tests\n"
        "test:\n"
        f"\tgo test -v -count=1 ./...\n"
        "\n"
        "# Run tests with race-condition detector\n"
        "test-race:\n"
        f"\tgo test -race -v ./...\n"
        "\n"
        + (
            "# Run tests with coverage\n"
            "test-cov:\n"
            f"\tgo test -v -coverprofile=coverage_{pkg}.out ./...\n"
            f"\tgo tool cover -func=coverage_{pkg}.out\n"
            if coverage else ""
        )
        + cov_target
        + "\n"
        "# Run go vet and staticcheck\n"
        "lint:\n"
        "\tgo vet ./...\n"
    )


# ---------------------------------------------------------------------------
# Top-level generator
# ---------------------------------------------------------------------------

def generate_unittest_scaffold(
    name: str,
    languages: str,
    framework: str,
    coverage: bool,
    output_dir: str,
) -> list:
    """Generate all unit-testing files for the requested languages.

    Returns a list of ``(Path, description)`` tuples for the written files.
    """
    out = Path(output_dir)
    written = []

    lang_list = [l.strip().lower() for l in languages.split(",") if l.strip()]

    for lang in lang_list:
        if lang not in SUPPORTED_LANGUAGES:
            print(f"Warning: unsupported language '{lang}' — skipping", file=sys.stderr)
            continue

        # Resolve framework for this language
        fw = framework.strip().lower() if framework.strip() else FRAMEWORK_DEFAULTS.get(lang, "")

        if lang == "python":
            _write(out / "pytest.ini", generate_pytest_ini(name, coverage))
            written.append((out / "pytest.ini", "pytest configuration"))

            _write(out / "conftest.py", generate_conftest_py(name))
            written.append((out / "conftest.py", "shared pytest fixtures"))

            _write(out / "tests" / "__init__.py", generate_python_tests_init())
            written.append((out / "tests" / "__init__.py", "test package marker"))

            _write(out / "tests" / "test_sample.py", generate_python_test_sample(name))
            written.append((out / "tests" / "test_sample.py", "sample Python unit tests"))

        elif lang in ("javascript", "typescript"):
            is_ts = lang == "typescript"
            if fw not in JS_FRAMEWORKS:
                fw = "jest"  # default JS framework

            if fw == "jest":
                _write(out / "jest.config.js", generate_jest_config(name, is_ts, coverage))
                written.append((out / "jest.config.js", "Jest configuration"))

            elif fw == "vitest":
                _write(out / "vitest.config.js", generate_vitest_config(name, coverage))
                written.append((out / "vitest.config.js", "Vitest configuration"))

            elif fw == "mocha":
                _write(out / ".mocharc.js", generate_mocha_rc(name, coverage))
                written.append((out / ".mocharc.js", "Mocha configuration"))

            ext = "ts" if is_ts else "js"
            test_file = out / "tests" / f"sample.test.{ext}"
            _write(test_file, generate_js_test_sample(name, fw, is_ts))
            written.append((test_file, f"sample {lang} unit tests ({fw})"))

        elif lang == "go":
            pkg = name.replace("-", "_").lower()
            test_file = out / f"{pkg}_test.go"
            _write(test_file, generate_go_test_sample(name))
            written.append((test_file, "sample Go unit tests"))

            _write(out / "Makefile.test", generate_go_makefile(name, coverage))
            written.append((out / "Makefile.test", "Go Makefile test targets"))

    return written


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------

def main():
    """CLI entry point."""
    args = parse_arguments()

    written = generate_unittest_scaffold(
        name=args.name,
        languages=args.languages,
        framework=args.framework,
        coverage=args.coverage,
        output_dir=args.output_dir,
    )

    if not written:
        print("No files generated. Check --languages value.", file=sys.stderr)
        sys.exit(1)

    print(f"Unit test scaffold generated in: {args.output_dir}/")
    for path, desc in written:
        print(f"  {path}  ({desc})")
    print()
    print("Languages:", args.languages)
    if args.framework:
        print("Framework override:", args.framework)
    print("Coverage enabled:", args.coverage)


if __name__ == "__main__":
    main()
