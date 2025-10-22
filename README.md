# plox

> This is my python version implementation of [crafting interpreter](https://craftinginterpreters.com/).

## Setup

I use [uv](https://docs.astral.sh/uv) to manage the environment. To set up the dev environment, just run

```bash
uv sync
```

## Run

```bash
python -m lox.lox --prompt                # Using REPL
python -m lox.lox --verbose               # Enable verbose logging
python -m lox.lox --path path/to/lox/file # Interpret a Lox script
```

## Test

```bash
pytest -q
```