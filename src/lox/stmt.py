from dataclasses import dataclass
from typing import List

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


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while(self)


@dataclass
class Break(Stmt):
    def accept(self, visitor: StmtVisitor):
        return visitor.visit_break(self)


@dataclass
class Continue(Stmt):
    def accept(self, visitor: StmtVisitor):
        return visitor.visit_continue(self)


@dataclass
class Function(Stmt):
    name: Token
    params: List[Token] = None
    body: List[Stmt] = None

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_function(self)


@dataclass
class Return(Stmt):
    keyword: Token
    value: Expr | None = None

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_return(self)
