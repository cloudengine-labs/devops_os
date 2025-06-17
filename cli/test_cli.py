import subprocess
import sys

def test_help():
    result = subprocess.run([sys.executable, "-m", "cli.devopsos", "--help"], capture_output=True, text=True)
    assert "Unified DevOps-OS CLI tool" in result.stdout

def test_scaffold_unknown():
    result = subprocess.run([sys.executable, "-m", "cli.devopsos", "scaffold", "unknown"], capture_output=True, text=True)
    assert "Unknown scaffold target" in result.stdout
