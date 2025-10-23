from dataclasses import dataclass, field
from typing import List

from lox.abc import ExprOrStmt
from lox.visitor import ExprVisitor
from lox.token import Token


@dataclass
class Binary(ExprOrStmt):
    left: ExprOrStmt
    op: Token
    right: ExprOrStmt

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary(self)


@dataclass
class Assign(ExprOrStmt):
    name: Token
    value: ExprOrStmt

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_assign(self)


@dataclass
class Call(ExprOrStmt):
    callee: ExprOrStmt
    paren: Token
    arguments: List[ExprOrStmt] = field(default_factory=list)

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_call(self)


@dataclass
class Get(ExprOrStmt):
    object: ExprOrStmt
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_get(self)


@dataclass
class Grouping(ExprOrStmt):
    expression: ExprOrStmt

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping(self)


@dataclass
class Literal(ExprOrStmt):
    value: object

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal(self)


@dataclass
class Logical(ExprOrStmt):
    left: ExprOrStmt
    op: Token
    right: ExprOrStmt

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_logical(self)


@dataclass
class Set(ExprOrStmt):
    object: ExprOrStmt
    name: Token
    value: ExprOrStmt

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_set(self)


@dataclass
class Super(ExprOrStmt):
    keyword: Token
    method: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_super(self)


@dataclass
class Self(ExprOrStmt):
    keyword: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_self(self)


@dataclass
class Unary(ExprOrStmt):
    op: Token
    right: ExprOrStmt

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary(self)


@dataclass
class Variable(ExprOrStmt):
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_variable(self)
