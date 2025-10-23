from dataclasses import dataclass


class Visitor:
    pass


@dataclass
class Expr:
    def accept(self, visitor: Visitor):
        raise NotImplementedError()


@dataclass
class Stmt:
    def accept(self, visitor: Visitor):
        raise NotImplementedError()
