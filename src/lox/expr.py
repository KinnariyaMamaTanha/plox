from dataclasses import dataclass, field
from typing import List

from lox.abc import Expr
from lox.token import Token
from lox.visitor import ExprVisitor


@dataclass
class Binary(Expr):
    left: Expr
    op: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary(self)


@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_assign(self)


@dataclass
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: List[Expr] = field(default_factory=list)

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_call(self)


@dataclass
class Get(Expr):
    object: Expr
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_get(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping(self)


@dataclass
class Literal(Expr):
    value: object

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal(self)


@dataclass
class Logical(Expr):
    left: Expr
    op: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_logical(self)


@dataclass
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_set(self)


@dataclass
class Super(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_super(self)


@dataclass
class Self(Expr):
    keyword: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_self(self)


@dataclass
class Unary(Expr):
    op: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary(self)


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_variable(self)
