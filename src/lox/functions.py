from __future__ import annotations

import time
from typing import TYPE_CHECKING, List

from lox.abc import LoxCallable
from lox.environment import Environment
from lox.error import ReturnException

if TYPE_CHECKING:
    from lox.interpreter import Interpreter
    from lox.stmt import Function


class Clock(LoxCallable):
    def __init__(self) -> None:
        pass

    def __call__(self, interpreter: Interpreter, argument: List[object]) -> object:
        return time.perf_counter()

    def arity(self) -> int:
        return 0

    def __str__(self) -> str:
        return "<native fn>"

    def __repr__(self) -> str:
        return self.__str__()


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        self.declaration = declaration
        self.closure: Environment = closure

    def __call__(self, interpreter: Interpreter, arguments: List[object]) -> object:
        environment: Environment = Environment(enclosing=self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            return return_value.value
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def __repr__(self) -> str:
        return self.__str__()
