from dataclasses import dataclass

from lox.abc import Expr, Stmt
from lox.token import Token
from lox.visitor import StmtVisitor


@dataclass
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block(self)


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


@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var(self)


@dataclass
class Assignment(Stmt):
    name: Token
    value: Expr

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_assignment(self)


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if(self)
