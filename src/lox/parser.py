from typing import List, Union

from lox.abc import Expr, Stmt
from lox.error import error
from lox.expr import (
    Assign,
    Binary,
    Call,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    This,
    Unary,
    Variable,
)
from lox.stmt import (
    Block,
    Break,
    Class,
    Continue,
    Expression,
    Function,
    If,
    Print,
    Return,
    Var,
    While,
)
from lox.token import Token, TokenType


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.loop_depth = 0

    def parse(self) -> List[Stmt]:
        statements = []
        while not self.finished:
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Stmt:
        """
        declaration → classDecl | varDecl | funDecl | statement ;
        """
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            elif self.match(TokenType.FUN):
                return self.function("function")
            elif self.match(TokenType.VAR):
                return self.var_decl()
            else:
                return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def class_declaration(self) -> Stmt:
        """
        classDecl → "class" IDENTIFIER "{" function* "}" ;
        """
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.finished:
            methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, methods)

    def function(self, kind: str) -> Stmt:
        """
        funDecl    → "fun" function ;
        function   → IDENTIFIER "(" parameters? ")" block ;
        parameters → IDENTIFIER ( "," IDENTIFIER )* ;
        """
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(
                        self.peek,
                        "Cannot have more than 255 parameters in a function.",
                    )
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)

    def var_decl(self) -> Stmt:
        """
        varDecl → "var" IDENTIFIER ( "=" expression )? ";" ;
        """
        name_token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name=name_token, initializer=initializer)

    def statement(self) -> Stmt:
        """
        statement → ifStmt | whileStmt | forStmt | breakStmt | continueStmt | exprStmt | printStmt | returnStmt | block ;
        """
        if self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.BREAK):
            return self.break_statement()
        elif self.match(TokenType.CONTINUE):
            return self.continue_statement()
        elif self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        else:
            return self.expression_statement()

    def return_statement(self) -> Stmt:
        """
        returnStmt → "return" expression? ";" ;
        """
        keyword = self.previous
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def block(self) -> List[Stmt]:
        """
        block → "{" declaration* "}" ;
        """
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.finished:
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def if_statement(self) -> Stmt:
        """
        ifStmt → "if" "(" expression ")" statement ( "else" statement )? ;
        """
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return If(condition, then_branch, else_branch)

    def break_statement(self) -> Stmt:
        """
        breakStmt → "break" ";" ;
        """
        if self.loop_depth == 0:
            raise self.error(self.previous, "Cannot use 'break' outside of a loop.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return Break()

    def continue_statement(self) -> Stmt:
        """
        continueStmt → "continue" ";" ;
        """
        if self.loop_depth == 0:
            raise self.error(self.previous, "Cannot use 'continue' outside of a loop.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'continue'.")
        return Continue()

    def while_statement(self) -> Stmt:
        """
        whileStmt → "while" "(" expression ")" statement ;
        """
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        try:
            self.loop_depth += 1
            body = self.statement()
            return While(condition, body)
        finally:
            self.loop_depth -= 1

    def for_statement(self) -> Stmt:
        """
        forStmt → "for" "(" ( varDecl | exprStmt | ";" ) expression? ";" expression? ")" statement ;
        """
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_decl()
        else:
            initializer = self.expression_statement()

        if self.match(TokenType.SEMICOLON):
            condition = None
        else:
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        if self.match(TokenType.SEMICOLON):
            increment = None
        else:
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        try:
            self.loop_depth += 1
            body = self.statement()

            if increment is not None:
                body = Block([body, Expression(increment)])

            if condition is None:
                condition = Literal(True)
            body = While(condition, body)

            if initializer is not None:
                body = Block([initializer, body])

            return body
        finally:
            self.loop_depth -= 1

    def print_statement(self) -> Stmt:
        """
        printStmt → "print" expression ";" ;
        """
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(expr)

    def expression_statement(self):
        """
        exprStmt → expression ";" ;
        """
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def expression(self) -> Expr:
        """
        expression → assignment ;
        """
        return self.assignment()

    def assignment(self) -> Expr:
        """
        assignment → ( call "." )? IDENTIFIER "=" assignment | logic_or ;
        """
        expr = self.logic_or()

        if self.match(TokenType.EQUAL):
            equals = self.previous
            value = self.assignment()

            if isinstance(expr, Variable):
                name_token = expr.name
                return Assign(name_token, value)
            elif isinstance(expr, Get):
                get: Get = expr
                return Set(get.object, get.name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def logic_or(self) -> Expr:
        """
        logic_or → logic_and ( "or" logic_and )*
        """
        expr = self.logic_and()
        while self.match(TokenType.OR):
            op = self.previous
            right = self.logic_and()
            expr = Logical(left=expr, op=op, right=right)
        return expr

    def logic_and(self) -> Expr:
        """
        logic_and → equality ( "and" equality )*
        """
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous
            right = self.equality()
            expr = Logical(left=expr, op=op, right=right)
        return expr

    def equality(self) -> Expr:
        """
        equality → comparison ( ( "!=" | "==" ) comparison )*
        """
        expr = self.comparison()

        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            op = self.previous
            right = self.comparison()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def comparison(self) -> Expr:
        """
        comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*
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
        term → factor ( ( "-" | "+" ) factor )*
        """
        expr = self.factor()

        while self.match([TokenType.MINUS, TokenType.PLUS]):
            op = self.previous
            right = self.factor()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def factor(self) -> Expr:
        """
        factor → unary ( ( "/" | "*" ) unary )*
        """
        expr = self.unary()

        while self.match([TokenType.SLASH, TokenType.STAR]):
            op = self.previous
            right = self.unary()
            expr = Binary(left=expr, op=op, right=right)

        return expr

    def unary(self) -> Expr:
        """
        unary → ( "!" | "-" ) unary | call
        """
        if self.match([TokenType.BANG, TokenType.MINUS]):
            op = self.previous
            right = self.unary()
            return Unary(op, right)

        return self.call()

    def call(self) -> Expr:
        """
        call → primary ( "(" arguments? ")" )* ;
        arguments → expression ( "," expression )* ;
        """
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(
                    TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                expr = Get(expr, name)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(
                        self.peek,
                        "Cannot have more than 255 arguments in a function call.",
                    )
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        """
        primary → NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER
        """
        if self.match(TokenType.FALSE):
            return Literal(False)
        elif self.match(TokenType.TRUE):
            return Literal(True)
        elif self.match(TokenType.NIL):
            return Literal(None)
        elif self.match([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self.previous.literal)
        elif self.match(TokenType.THIS):
            return This(self.previous)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        elif self.match(TokenType.IDENTIFIER):
            return Variable(self.previous)
        elif self.match(TokenType.PLUS):
            self.error(self.previous, "Missing left-hand operand.")
            self.term()
            return None
        elif self.match(
            [
                TokenType.SLASH,
                TokenType.STAR,
            ]
        ):
            self.error(self.previous, "Missing left-hand operand.")
            self.factor()
            return None
        elif self.match(
            [
                TokenType.EQUAL_EQUAL,
                TokenType.BANG_EQUAL,
            ]
        ):
            self.error(self.previous, "Missing left-hand operand.")
            self.equality()
            return None
        elif self.match(
            [
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
            ]
        ):
            self.error(self.previous, "Missing left-hand operand.")
            self.comparison()
            return None

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
