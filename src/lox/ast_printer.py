from typing import List, Union

from lox.abc import Expr
from lox.expr import Binary, Grouping, Literal, Unary
from lox.visitor import ExprVisitor


class AstPrinter(ExprVisitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_binary(self, expr: Binary) -> str:
        return self.parenthesize(expr.op.lexeme, [expr.left, expr.right])

    def visit_grouping(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary(self, expr: Unary) -> str:
        return self.parenthesize(expr.op.lexeme, expr.right)

    def parenthesize(self, name: str, exprs: Union[Expr, List[Expr]]) -> str:
        if not isinstance(exprs, list):
            exprs = [exprs]
        result = f"({name}"
        for expr in exprs:
            result += " "
            result += expr.accept(self)
        result += ")"
        return result
