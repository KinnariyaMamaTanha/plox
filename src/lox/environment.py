from dataclasses import dataclass, field

from lox.error import PloxRuntimeError
from lox.token import Token


@dataclass
class Environment:
    mapping: dict = field(default_factory=dict)
    enclosing: "Environment | None" = None

    def define(self, name: str, value: object) -> None:
        self.mapping[name] = value

    def get(self, name: Token):
        if name.lexeme in self.mapping:
            return self.mapping[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.mapping:
            self.mapping[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
