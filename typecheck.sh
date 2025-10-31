#!/bin/bash
set -e
pip install -q -e .[test,typecheck]
ty check src tests
