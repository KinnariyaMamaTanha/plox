class Visitor:
    pass


class Expr:
    def accept(self, visitor: Visitor):
        raise NotImplementedError()


class Stmt:
    def accept(self, visitor: Visitor):
        raise NotImplementedError()
