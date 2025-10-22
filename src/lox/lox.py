import argparse
import logging
from typing import List, Union

from lox.scanner import Scanner
from lox.token import Token, TokenType
from utils import validate_args

had_error = False

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
    global had_error
    if had_error:
        exit(65)


def run_prompt():
    """
    Start a REPL (Read-Eval-Print Loop) for Lox.
    """
    global had_error
    while True:
        try:
            source: str = input("plox> ")
            if source == "exit":
                break
            run(source)
            had_error = False
        except EOFError:
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")


def run(source: str):
    scanner = Scanner(source)
    tokens: List[Token] = scanner.scan_tokens()

    # For demonstration, just print the tokens
    for token in tokens:
        print(token)


def error(line_or_token: Union[int, Token], message: str) -> None:
    if isinstance(line_or_token, int):
        report(line_or_token, "", message)
    elif isinstance(line_or_token, Token):
        if line_or_token.type == TokenType.EOF:
            report(line_or_token.line, "at end", message)
        else:
            report(line_or_token.line, f"at '{line_or_token.lexeme}'", message)
    else:
        raise TypeError("line_or_token must be a Token or a string")


def report(line: int, where: str, message: str) -> None:
    logger.error(f"[line {line}] Error {where}: {message}")
    global had_error
    had_error = True


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

    args = parser.parse_args()
    main(args)
