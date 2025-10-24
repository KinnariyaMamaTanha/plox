from dataclasses import dataclass

from lox.abc import Expr, Stmt
from lox.visitor import StmtVisitor


@dataclass
class Block(Stmt):
    pass


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print(self)
