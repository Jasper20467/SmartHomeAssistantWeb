"""
Pytest configuration — adds LineBotAI root to sys.path so that
`agent`, `services`, `Home_assistant`, `config` packages can be imported
when running `pytest` from the LineBotAI directory.
"""
import sys
import os

# Ensure LineBotAI/ is importable regardless of where pytest is invoked from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
