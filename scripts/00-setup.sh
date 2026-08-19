#!/bin/bash

if [ ! -e .venv ]; then
  uv venv --python 3.14 --seed .venv
  source .venv/bin/activate
  pip install -e .
fi
