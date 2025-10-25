import argparse
import logging
from typing import List

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from lox import error
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.resolver import Resolver
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
    if error.has_error:
        exit(65)
    if error.has_runtime_error:
        exit(70)


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


def is_complete_source(source: str) -> bool:
    """Heuristic check to see if the given source is a complete Lox input.

    Rules (basic, not string-aware):
    - Track parentheses and braces balance across lines.
    - Consider input complete when both balances are zero AND the last
      non-comment, non-whitespace significant character is ';' or '}'.
    """
    paren = 0
    brace = 0
    last_sig = ""

    for raw_line in source.splitlines():
        line = raw_line.split("//", 1)[0]
        paren += line.count("(") - line.count(")")
        brace += line.count("{") - line.count("}")
        s = line.rstrip()
        if s:
            last_sig = s[-1]

    if paren == 0 and brace == 0 and last_sig in {";", "}"}:
        return True
    return False


def run(source: str, interpreter: Interpreter | None = None):
    scanner = Scanner(source)
    tokens: List[Token] = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
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
