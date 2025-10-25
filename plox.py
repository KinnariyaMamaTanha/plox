import argparse
import logging
import sys
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from lox import error
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.resolver import Resolver
from lox.scanner import Scanner
from lox.token import Token
from utils import is_complete_source, validate_args

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace):
    """Entrypoint for the CLI.

    Behavior:
    - No positional arguments -> start REPL (run_prompt)
    - One positional argument (FILE) -> execute file (run_file)
    - --verbose enables DEBUG-level logs
    """
    logger.debug(f"Parsed args: {args}")
    validate_args(args)

    # Only positional FILE is supported
    path = getattr(args, "file", None)

    if path:
        logger.debug(f"Running file: {path}")
        run_file(path)
    else:
        logger.debug("Starting REPL (run_prompt)")
        run_prompt()


def run_file(path):
    """
    Execute a Lox script from a file.
    """
    logger.debug(f"Reading file from path: {path}")
    with open(path, "r") as file:
        source = file.read()
    logger.debug(f"Read {len(source)} characters from file")
    run(source)
    if error.has_error:
        sys.exit(65)
    if error.has_runtime_error:
        sys.exit(70)


def run_prompt():
    """
    Start a REPL (Read-Eval-Print Loop) for Lox.
    """
    history = InMemoryHistory()
    print("======================================================")
    print("Welcome to plox! Press Ctrl+D or type 'exit' to leave.")
    print("======================================================")

    interpreter = Interpreter()

    # Accumulate lines until the input is a complete statement/block
    buffer: str = ""

    while True:
        try:
            prompt_label = "plox> " if not buffer else "...   "
            line: str = prompt(prompt_label, history=history)

            # Allow exiting only when not in the middle of a multi-line entry
            if not buffer and line.strip() == "exit":
                break

            # Ignore pure empty inputs if nothing in buffer yet
            if not buffer and not line.strip():
                continue

            buffer += line + "\n"

            if is_complete_source(buffer):
                logger.debug(f"Executing REPL buffer with {len(buffer)} characters")
                run(buffer, interpreter=interpreter)
                # Reset compile-time error flag for the next REPL input
                error.has_error = False
                buffer = ""
        except EOFError:
            break
        except KeyboardInterrupt:
            # On Ctrl+C, clear current buffer and start over
            buffer = ""
            continue
        except Exception as e:
            logger.error(f"An error occurred: {e}")


def run(source: str, interpreter: Interpreter | None = None):
    scanner = Scanner(source)
    tokens: List[Token] = scanner.scan_tokens()
    logger.debug(f"Scanned {len(tokens)} tokens")
    parser = Parser(tokens)
    statements = parser.parse()
    logger.debug(
        "Parser returned %s statements" % (len(statements) if statements else 0)
    )
    if error.has_error:
        return

    _interpreter = interpreter or Interpreter()
    _interpreter.locals.clear()
    resolver = Resolver(_interpreter)
    resolver.resolve(statements)
    if error.has_error:
        return

    _interpreter.interpret(statements)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Optional positional FILE argument; if provided, we run the file.
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Path to the Lox script to execute (positional)",
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Enable verbose logging"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    main(args)
