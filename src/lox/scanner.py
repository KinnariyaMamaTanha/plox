from typing import List

from lox.error import error
from lox.token import Token, TokenType


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: List[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    def scan_tokens(self) -> List[Token]:
        while not self.finished:
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))

        return self.tokens

    def scan_token(self) -> None:
        c: str = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)
            case "!":
                self.add_token(
                    TokenType.BANG_EQUAL if self._advance_cmp("=") else TokenType.BANG
                )
            case "=":
                self.add_token(
                    TokenType.EQUAL_EQUAL if self._advance_cmp("=") else TokenType.EQUAL
                )
            case "<":
                self.add_token(
                    TokenType.LESS_EQUAL if self._advance_cmp("=") else TokenType.LESS
                )
            case ">":
                self.add_token(
                    TokenType.GREATER_EQUAL
                    if self._advance_cmp("=")
                    else TokenType.GREATER
                )
            case "/":
                if self._advance_cmp("/"):
                    # A comment goes until the end of the line.
                    while self.peek != "\n" and not self.finished:
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self.scan_string()
            case _:
                if c.isdigit():
                    self.scan_number()
                elif c.isalpha() or c == "_":
                    self.scan_identifier()
                else:
                    error(self.line, "Unexpected character.")

    def scan_number(self) -> None:
        while self.peek.isdigit():
            self.advance()

        if self.peek == "." and self.peek_next.isdigit():
            self.advance()  # consume the "."
            while self.peek.isdigit():
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start : self.current]))

    def scan_identifier(self) -> None:
        while self.peek.isalnum() or self.peek == "_":
            self.advance()

        text = self.source[self.start : self.current]
        type = self.keywords.get(text)
        if type is None:
            type = TokenType.IDENTIFIER

        self.add_token(type)

    def scan_string(self):
        while self.peek != '"' and not self.finished:
            if self.peek == "\n":
                self.line += 1
            self.advance()
        if self.finished:
            error(self.line, "Unterminated string.")
            return

        self.advance()  # The closing ".
        s: str = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, s)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def add_token(self, type: TokenType, literal: object = None) -> None:
        text: str = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def _advance_cmp(self, expected: str) -> bool:
        if self.finished:
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    @property
    def peek(self) -> str:
        return "\0" if self.finished else self.source[self.current]

    @property
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    @property
    def finished(self) -> bool:
        return self.current >= len(self.source)
