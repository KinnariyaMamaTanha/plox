from lox.error import PloxRuntimeError
from lox.token import Token


class Environment:
    def __init__(self) -> None:
        self.mapping = {}

    def define(self, name: str, value: object) -> None:
        self.mapping[name] = value

    def get(self, name: Token):
        if name.lexeme in self.mapping:
            return self.mapping[name.lexeme]
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.mapping:
            self.mapping[name.lexeme] = value
            return
        raise PloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def __str__(self) -> str:
        return str(self.mapping)

    def __repr__(self) -> str:
        return f"Environment({self.mapping})"
