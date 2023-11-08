#!/bin/bash

export PYTHONPATH='src':$PYTHONPATH

docker compose down
docker compose up -d
sleep 1

docker exec -it client python -m src.client docker

docker compose down
