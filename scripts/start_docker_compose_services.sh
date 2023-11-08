#!/bin/bash

export PYTHONPATH='src':$PYTHONPATH

python -m src.client
python -m src.server
