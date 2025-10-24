from dataclasses import dataclass, field

from lox.error import PloxRuntimeError
from lox.token import Token


@dataclass
class Environment:
    values: dict = field(default_factory=dict)
    enclosing: "Environment | None" = None

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values[name]

    def ancestor(self, distance: int) -> "Environment":
        environment = self
        for _ in range(distance):
            if environment.enclosing is None:
                break
            environment = environment.enclosing

        return environment

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self.ancestor(distance).values[name.lexeme] = value
