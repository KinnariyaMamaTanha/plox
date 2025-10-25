from __future__ import annotations

import time
from typing import TYPE_CHECKING, Dict, List

from lox.abc import LoxCallable
from lox.environment import Environment
from lox.error import ReturnException
from lox.token import Token

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
    def __init__(
        self, declaration: Function, closure: Environment, is_initializer: bool
    ) -> None:
        self.declaration = declaration
        self.closure: Environment = closure
        self.is_initializer = is_initializer

    def __call__(self, interpreter: Interpreter, arguments: List[object]) -> object:
        environment: Environment = Environment(enclosing=self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

    def __repr__(self) -> str:
        return self.__str__()

    def bind(self, instance: LoxInstance):
        env = Environment(enclosing=self.closure)
        env.define("this", instance)
        return LoxFunction(self.declaration, env, self.is_initializer)


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: Dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods

    def __str__(self) -> str:
        return f"<class {self.name}>"

    def __repr__(self) -> str:
        return self.__str__()

    def __call__(self, interpreter: Interpreter, argument: List[object]) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance)(interpreter, argument) # first bind 'this' then call
        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is not None:
            return initializer.arity()
        return 0

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self.methods:
            return self.methods[name]
        return None


class LoxInstance(LoxCallable):
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.fields: Dict[str, object] = {}

    def __str__(self) -> str:
        return f"<instance of {self.klass.name}>"

    def __repr__(self) -> str:
        return self.__str__()

    def __getitem__(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise Exception(f"Undefined property '{name.lexeme}'.")

    def __setitem__(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value
