import logging
from typing import Union

from lox.token import Token, TokenType

logger = logging.getLogger(__name__)

has_error = False  # global error flag
has_runtime_error = False  # global runtime error flag


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
    global has_error
    has_error = True


class PloxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.message = message


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class ReturnException(Exception):
    def __init__(self, value: object):
        self.value = value


def runtime_error(error: PloxRuntimeError):
    logger.error(error.message + f"\n[line {error.token.line}]")
    global has_runtime_error
    has_runtime_error = True
