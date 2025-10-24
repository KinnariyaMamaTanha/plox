from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class Visitor:
    pass


@dataclass(eq=False)
class Expr:
    def accept(self, visitor: Visitor):
        raise NotImplementedError()


@dataclass
class Stmt:
    def accept(self, visitor: Visitor):
        raise NotImplementedError()


class LoxCallable:
    def __init__(self, callee: Expr) -> None:
        pass

    def __call__(self, interpreter: Interpreter, argument: List[object]) -> object:
        pass

    def arity(self) -> int:
        pass
