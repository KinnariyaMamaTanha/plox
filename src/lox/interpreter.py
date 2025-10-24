from typing import List, Union

from lox.abc import Expr, Stmt
from lox.error import PloxRuntimeError, runtime_error
from lox.expr import Binary, Literal, Unary
from lox.token import Token, TokenType
from lox.visitor import ExprVisitor, StmtVisitor


class Interpreter(ExprVisitor, StmtVisitor):
    def visit_print(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    def visit_expression(self, stmt):
        value = self.evaluate(stmt.expression)
        return None

    def visit_literal(self, expr: Literal):
        return expr.value

    def visit_grouping(self, expr):
        return self.evaluate(expr.expression)

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def visit_unary(self, expr: Unary):
        right = self.evaluate(expr.right)

        if expr.op.type == TokenType.MINUS:
            return -float(right)
        elif expr.op.type == TokenType.BANG:
            return not self._is_truthy(right)

        return None

    def _is_truthy(self, value: object):
        """
        In Lox, false and nil are falsey, and everything else is truthy.
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value

        return True

    def visit_binary(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.op.type:
            case TokenType.MINUS:
                self.check(expr.op, [left, right])
                return left - right
            case TokenType.STAR:
                self.check(expr.op, [left, right])
                return left * right
            case TokenType.SLASH:
                self.check(expr.op, [left, right])
                if right == 0:
                    raise PloxRuntimeError(expr.op, "Division by zero.")
                return left / right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise PloxRuntimeError(
                    expr.op, "Operands must be two numbers or two strings."
                )
            case TokenType.BANG_EQUAL:
                # Since strings can be compared directly in Python, there is no need to check types here.
                # Same for EQUAL_EQUAL, GREATER, GREATER_EQUAL, LESS, LESS_EQUAL, etc.
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.GREATER:
                return left > right
            case TokenType.GREATER_EQUAL:
                return left >= right
            case TokenType.LESS:
                return left < right
            case TokenType.LESS_EQUAL:
                return left <= right
            case TokenType.COMMA:
                return right
            case TokenType.AND:
                return self._is_truthy(left) and self._is_truthy(right)
            case TokenType.OR:
                return self._is_truthy(left) or self._is_truthy(right)

    def check(self, operator: Token, operands: Union[object, List[object]]):
        if not isinstance(operands, list):
            operands = [operands]
        for op in operands:
            if not isinstance(op, float):
                raise PloxRuntimeError(operator, "Operand must be a number.")

    def interpret(self, stmts: Union[Stmt, List[Stmt]]):
        if not isinstance(stmts, list):
            stmts = [stmts]

        for stmt in stmts:
            try:
                self.execute(stmt)
            except PloxRuntimeError as error:
                runtime_error(error)

    def execute(self, stmt: Stmt):
        stmt.accept(self)

    def stringify(self, value: object):
        if value is None:
            return "nil"

        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text

        return str(value)
