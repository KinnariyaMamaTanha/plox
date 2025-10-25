# plox

> This is my python version implementation of [crafting interpreter](https://craftinginterpreters.com/).

## Setup

I use [uv](https://docs.astral.sh/uv) to manage the environment. To set up the dev environment, just run

```bash
uv sync
source .venv/bin/activate
```

## Run

```bash
# Start REPL (no args)
python plox.py

# Run a Lox script (positional path)
python plox.py path/to/script.lox

# Enable verbose logs (DEBUG)
python plox.py --verbose path/to/script.lox
```

## Test

```bash
pytest -q
```

## Build

```bash
pyinstaller --onefile plox.py --name plox --clean
```

Then you can find the `plox` executable in folder `./dist`.

You can also run the binary with the same conventions:

```bash
./dist/plox                 # REPL
./dist/plox script.lox      # Run a file
./dist/plox --verbose file.lox
```