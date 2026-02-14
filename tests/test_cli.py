"""Tests for the CLI interface (python transcribe.py ...)."""

import subprocess
import sys


def test_help_flag():
    r = subprocess.run([sys.executable, "transcribe.py", "--help"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "Usage:" in r.stdout
    assert "fast" in r.stdout


def test_no_args_shows_help():
    r = subprocess.run([sys.executable, "transcribe.py"], capture_output=True, text=True)
    assert r.returncode == 0
    assert "Usage:" in r.stdout


def test_missing_file_exits_1():
    r = subprocess.run([sys.executable, "transcribe.py", "nope.m4a"], capture_output=True, text=True)
    assert r.returncode == 1
    assert "not found" in r.stdout.lower()
