from dataclasses import dataclass, field
from typing import List

from lox.abc import Expr
from lox.token import Token
from lox.visitor import ExprVisitor


@dataclass(eq=False)
class Binary(Expr):
    left: Expr
    op: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_binary(self)


@dataclass(eq=False)
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_assign(self)


@dataclass(eq=False)
class Call(Expr):
    callee: Expr
    paren: Token  # Token for the closing parenthesis
    arguments: List[Expr] = field(default_factory=list)

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_call(self)


@dataclass(eq=False)
class Get(Expr):
    object: Expr
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_get(self)


@dataclass(eq=False)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_grouping(self)


@dataclass(eq=False)
class Literal(Expr):
    value: object

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_literal(self)


@dataclass(eq=False)
class Logical(Expr):
    left: Expr
    op: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_logical(self)


@dataclass(eq=False)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_set(self)


@dataclass(eq=False)
class Super(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_super(self)


@dataclass(eq=False)
class This(Expr):
    keyword: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_this(self)


@dataclass(eq=False)
class Unary(Expr):
    op: Token
    right: Expr

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_unary(self)


@dataclass(eq=False)
class Variable(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor):
        return visitor.visit_variable(self)
