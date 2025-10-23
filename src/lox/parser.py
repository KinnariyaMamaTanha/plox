from typing import List, Union

from lox.abc import Expr
from lox.error import error
from lox.expr import Binary, Grouping, Literal, Unary
from lox.token import Token, TokenType


class ParseError(RuntimeError):
    pass


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None

    def expression(self) -> Expr:
        """
        expression → equality
        """
        return self.equality()

    def equality(self) -> Expr:
        """
        equality → comparison ( ( "!=" | "==" ) comparison )* ;
        """
        expr = self.comparison()

        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            op = self.previous
            right = self.comparison()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def comparison(self) -> Expr:
        """
        comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
        """
        expr = self.term()

        while self.match(
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ]
        ):
            op = self.previous
            right = self.term()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def term(self) -> Expr:
        """
        term → factor ( ( "-" | "+" ) factor )* ;
        """
        expr = self.factor()

        while self.match([TokenType.MINUS, TokenType.PLUS]):
            op = self.previous
            right = self.factor()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def factor(self) -> Expr:
        """
        factor → unary ( ( "/" | "*" ) unary )* ;
        """
        expr = self.unary()

        while self.match([TokenType.SLASH, TokenType.STAR]):
            op = self.previous
            right = self.unary()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def unary(self) -> Expr:
        """
        unary → ( "!" | "-" ) unary | primary ;
        """
        if self.match([TokenType.BANG, TokenType.MINUS]):
            op = self.previous
            right = self.unary()
            return Unary(op, right)

        return self.primary()

    def primary(self) -> Expr:
        """
        primary → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" ;
        """
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self.previous.literal)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek, "Expect expression.")

    def match(self, types: Union[TokenType, List[TokenType]]):
        if not isinstance(types, list):
            types = [types]

        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        if self.finished:
            return False

        return self.peek.type == type

    def advance(self):
        if not self.finished:
            self.current += 1
        return self.previous

    def consume(self, type: TokenType, message: str = ""):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek, message)

    def error(self, token: Token, message: str):
        error(token, message)
        return ParseError()

    def synchronize(self):
        """
        Discards tokens until it reaches a statement boundary.
        """
        self.advance()

        while not self.finished:
            if self.previous.type == TokenType.SEMICOLON:
                return

            if self.peek.type in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

            self.advance()

    @property
    def finished(self) -> bool:
        return self.peek.type == TokenType.EOF

    @property
    def peek(self) -> Token:
        return self.tokens[self.current]

    @property
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
