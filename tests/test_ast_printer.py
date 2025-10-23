from lox.ast_printer import AstPrinter
from lox.expr import Binary, Grouping, Literal, Unary
from lox.token import Token, TokenType


def make_token(t: TokenType, lexeme: str):
    return Token(type=t, lexeme=lexeme, literal=None, line=1)


def test_prints_unary_and_grouping_and_binary():
    # Builds: (* (- 123) (group 45.67))
    expr = Binary(
        left=Unary(op=make_token(TokenType.MINUS, "-"), right=Literal(123)),
        op=make_token(TokenType.STAR, "*"),
        right=Grouping(expression=Literal(45.67)),
    )

    out = AstPrinter().print(expr)
    assert out == "(* (- 123) (group 45.67))"


def test_prints_nil_for_none_literal():
    expr = Literal(None)
    out = AstPrinter().print(expr)
    assert out == "nil"


def test_prints_string_literal_without_quotes():
    expr = Literal("hello")
    out = AstPrinter().print(expr)
    # AstPrinter.str(value) prints without quotes
    assert out == "hello"


def test_nested_binary_expression():
    # (+ 1 (* 2 3))
    expr = Binary(
        left=Literal(1),
        op=make_token(TokenType.PLUS, "+"),
        right=Binary(
            left=Literal(2),
            op=make_token(TokenType.STAR, "*"),
            right=Literal(3),
        ),
    )

    out = AstPrinter().print(expr)
    assert out == "(+ 1 (* 2 3))"
