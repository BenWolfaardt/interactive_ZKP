# App

Description.

## Local Setup and Configuration

Things to know to get up and running.

### Run Locally

Setting up our environment

```sh
  poetry install
  poetry shell
```

> `python -m src --env <choice>`

See `python -m src -h` for a list of choices.

### Run Tests

Then run dependencies with pytest:

```sh
  poetry run pytest tests/
```

### Pre-commit

> To be setup before commiting any code.

Setup and run the pre-commit (uses .pre-commit-config.yaml):

```sh
  pre-commit install
  pre-commit run --all-files
```

> The above needs to be performed from within the virtual environment otherwise pre-pend with `poetry run`

## Ideas

- Idea_1

## Todos

- [ ] Todo_1
