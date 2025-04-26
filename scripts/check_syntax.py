#!/usr/bin/env python3
import ast
import sys

def check_syntax(filename):
    """Check Python file for syntax errors"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        ast.parse(source)
        print(f"✅ {filename} has valid syntax")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"  Line {e.lineno}, column {e.offset}: {e.text.strip()}")
        print(f"  {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_syntax.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    if not check_syntax(filename):
        sys.exit(1) 