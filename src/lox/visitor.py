from lox.abc import Visitor


class ExprVisitor(Visitor):
    def visit_binary(self, expr):
        pass

    def visit_assign(self, expr):
        pass

    def visit_call(self, expr):
        pass

    def visit_get(self, expr):
        pass

    def visit_grouping(self, expr):
        pass

    def visit_literal(self, expr):
        pass

    def visit_logical(self, expr):
        pass

    def visit_set(self, expr):
        pass

    def visit_super(self, expr):
        pass

    def visit_self(self, expr):
        pass

    def visit_unary(self, expr):
        pass

    def visit_variable(self, expr):
        pass


class StmtVisitor(Visitor):
    def visit_print(self, stmt):
        pass

    def visit_expression(self, stmt):
        pass

    def visit_var(self, stmt):
        pass

    def visit_assignment(self, stmt):
        pass

    def visit_block(self, stmt):
        pass

    def visit_if(self, stmt):
        pass
