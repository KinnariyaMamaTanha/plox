from typing import List, Union

from lox.abc import Expr, Stmt
from lox.environment import Environment
from lox.error import (
    BreakException,
    ContinueException,
    PloxRuntimeError,
    ReturnException,
    runtime_error,
)
from lox.expr import Assign, Binary, Call, Grouping, Literal, Unary, Variable
from lox.functions import Clock, LoxCallable, LoxFunction
from lox.stmt import (
    Block,
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
from lox.visitor import ExprVisitor, StmtVisitor


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self) -> None:
        self.globals = Environment()
        self.environment = self.globals

        self.globals.define("clock", Clock())

    def visit_print(self, stmt: Print):
        value = self.evaluate(stmt.expression)
        if isinstance(value, bool):
            print("true" if value else "false")
        else:
            print(self.stringify(value))
        return None

    def visit_expression(self, stmt: Expression):
        value = self.evaluate(stmt.expression)
        return None

    def visit_var(self, stmt: Var):
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        else:
            value = None
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_block(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(enclosing=self.environment))
        return None

    def visit_if(self, stmt: If):
        if self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_logical(self, expr: Binary):
        left = self.evaluate(expr.left)

        if expr.op.type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        right = self.evaluate(expr.right)
        return right

    def visit_while(self, stmt: While):
        while self._is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except ContinueException:
                # Skip remainder of the body and reevaluate condition
                continue
            except BreakException:
                break
        return None

    def visit_break(self, stmt):
        raise BreakException()

    def visit_continue(self, stmt: Continue):
        raise ContinueException()

    def execute_block(self, statements: List[Stmt], environment: Environment):
        previous_env = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous_env

    def visit_variable(self, expr: Variable):
        return self.environment.get(expr.name)

    def visit_assign(self, expr: Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_literal(self, expr: Literal):
        return expr.value

    def visit_grouping(self, expr: Grouping):
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

    def visit_call(self, expr: Call):
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LoxCallable):
            raise PloxRuntimeError(expr.paren, "Can only call functions and classes.")
        func: LoxCallable = callee
        if len(arguments) != func.arity():
            raise PloxRuntimeError(
                expr.paren,
                f"Expected {func.arity()} arguments but got {len(arguments)}.",
            )
        return func(self, arguments)

    def visit_function(self, stmt: Function):
        fun = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, fun)
        return None

    def visit_return(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

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
