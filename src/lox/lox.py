import argparse
import logging
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from lox.error import has_error
from lox.scanner import Scanner
from lox.token import Token
from utils import validate_args

logger = logging.getLogger(__name__)


def main(args: argparse.Namespace):
    validate_args(args)
    if args.path:
        run_file(args.path)
    else:
        run_prompt()


def run_file(path):
    """
    Execute a Lox script from a file.
    """
    with open(path, "r") as file:
        source = file.read()
    run(source)
    global has_error
    if has_error:
        exit(65)


def run_prompt():
    """
    Start a REPL (Read-Eval-Print Loop) for Lox.
    """
    global has_error
    history = InMemoryHistory()
    print("======================================================")
    print("Welcome to plox! Press Ctrl+D or type 'exit' to leave.")
    print("======================================================")

    while True:
        try:
            source: str = prompt("plox> ", history=history)
            if source.strip() == "exit":
                break
            if source.strip():
                run(source)
                has_error = False
        except EOFError:
            break
        except KeyboardInterrupt:
            continue
        except Exception as e:
            logger.error(f"An error occurred: {e}")


def run(source: str):
    scanner = Scanner(source)
    tokens: List[Token] = scanner.scan_tokens()

    for token in tokens:
        print(token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        default=None,
        type=str,
        help="Path to the Lox script to execute",
    )
    parser.add_argument(
        "--prompt", action="store_true", default=False, help="Start REPL mode"
    )
    parser.add_argument(
        "--verbose", action="store_true", default=False, help="Enable verbose logging"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="[pid=%(process)d %(asctime)s %(levelname)s] %(filename)s, line %(lineno)d: %(message)s",
    )

    main(args)
