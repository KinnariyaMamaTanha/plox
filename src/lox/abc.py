from abc import ABC, abstractmethod


class Visitor(ABC):
    pass


class ExprOrStmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass
