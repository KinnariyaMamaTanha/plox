from enum import Enum
from typing import Dict, List, Union

from lox.abc import Expr, Stmt
from lox.error import error
from lox.expr import Assign, Binary, Call, Grouping, Literal, Logical, Unary, Variable
from lox.interpreter import Interpreter
from lox.stmt import Block, Expression, Function, If, Print, Return, Var, While
from lox.token import Token
from lox.visitor import ExprVisitor, StmtVisitor


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1
    INITIALIZER = 2


class Resolver(ExprVisitor, StmtVisitor):
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        # In each scope, map variable -> is defined
        # true -> defined, false -> declared but not defined; not exist -> not declared
        self.scopes: List[Dict[str, bool]] = []
        self.current_func = FunctionType.NONE

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def resolve(self, statements: List[Stmt]):
        for statement in statements:
            self._resolve(statement)

    def _resolve_local(self, expr: Expr, name: Token):
        for i, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, i)
                return

    def _resolve_function(self, func: Function, func_type: FunctionType):
        enclosing_func = self.current_func
        self.current_func = func_type
        self.begin_scope()
        for param in func.params:
            self.declare(param)
            self.define(param)
        self.resolve(func.body)
        self.end_scope()
        self.current_func = enclosing_func

    def _resolve(self, expr_or_stmt: Union[Expr, Stmt]):
        expr_or_stmt.accept(self)

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return
        scope = self.scopes[-1]
        if scope.get(name.lexeme) is not None:
            error(name, "Variable with this name already declared in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token):
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = True

    def visit_block(self, stmt: Block):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_var(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_return(self, stmt: Return):
        if self.current_func == FunctionType.NONE:
            error(stmt.keyword, "Cannot return from top-level code.")

        if stmt.value is not None:
            if self.current_func == FunctionType.INITIALIZER:
                error(stmt.keyword, "Cannot return a value from an initializer.")
            self._resolve(stmt.value)

    def visit_variable(self, expr: Variable):
        if len(self.scopes) != 0 and self.scopes[-1].get(expr.name.lexeme) is False:
            error(expr.name, "Cannot read local variable in its own initializer.")
        self._resolve_local(expr, expr.name)

    def visit_assign(self, expr: Assign):
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_function(self, stmt: Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression(self, stmt: Expression):
        self._resolve(stmt.expression)

    def visit_if(self, stmt: If):
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_print(self, stmt: Print):
        self._resolve(stmt.expression)

    def visit_while(self, stmt: While):
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_binary(self, expr: Binary):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call(self, expr: Call):
        self._resolve(expr.callee)
        for argument in expr.arguments:
            self._resolve(argument)

    def visit_grouping(self, expr: Grouping):
        self._resolve(expr.expression)

    def visit_literal(self, expr: Literal):
        pass

    def visit_logical(self, expr: Logical):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_unary(self, expr: Unary):
        self._resolve(expr.right)
