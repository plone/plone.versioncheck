#!/bin/bash
set -e

# Ensure we're in a venv or create one
if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d .venv ]; then
        uv venv
    fi
    source .venv/bin/activate
fi

uv pip install -q -e .[test,typecheck]
pyright src
