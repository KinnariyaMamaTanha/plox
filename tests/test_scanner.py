import pytest

from lox.scanner import Scanner
from lox.token import TokenType


def tokens_summary(tokens):
    return [(t.type, t.lexeme, t.literal) for t in tokens]


def test_scan_tokens_mixed_source():
    # Mixed source with keywords, identifiers, operators, numbers, strings, comments
    source = 'var x = 123;\nprint "hi"; // say hi\nx == 123.45 and x != 0\n'

    scanner = Scanner(source)
    toks = scanner.scan_tokens()

    # Extract token triplets (type, lexeme, literal)
    summary = tokens_summary(toks)

    # Expect lexemes without leading whitespace now
    expected = [
        (TokenType.VAR, "var", None),
        (TokenType.IDENTIFIER, "x", None),
        (TokenType.EQUAL, "=", None),
        (TokenType.NUMBER, "123", pytest.approx(123)),
        (TokenType.SEMICOLON, ";", None),
        (TokenType.PRINT, "print", None),
        (TokenType.STRING, '"hi"', "hi"),
        (TokenType.SEMICOLON, ";", None),
        (TokenType.IDENTIFIER, "x", None),
        (TokenType.EQUAL_EQUAL, "==", None),
        (TokenType.NUMBER, "123.45", pytest.approx(123.45)),
        (TokenType.AND, "and", None),
        (TokenType.IDENTIFIER, "x", None),
        (TokenType.BANG_EQUAL, "!=", None),
        (TokenType.NUMBER, "0", pytest.approx(0)),
        (TokenType.EOF, "", None),
    ]

    assert summary == expected


def test_scan_token_single_call_sequences():
    # Test scanning exactly one token via scan_token()
    # 1) Two-character operator '=='
    scanner = Scanner("==")
    scanner.start = scanner.current
    scanner.scan_token()
    assert len(scanner.tokens) == 1
    assert scanner.tokens[0].type == TokenType.EQUAL_EQUAL
    assert scanner.tokens[0].lexeme == "=="

    # 2) Single-character '!' when not followed by '=' becomes BANG
    scanner = Scanner("! ")
    scanner.start = scanner.current
    scanner.scan_token()
    assert len(scanner.tokens) == 1
    assert scanner.tokens[0].type == TokenType.BANG
    assert scanner.tokens[0].lexeme == "!"


def test_scan_keyword_continue():
    scanner = Scanner("continue;")
    toks = scanner.scan_tokens()
    types = [t.type for t in toks]
    assert types[0] == TokenType.CONTINUE
    assert toks[0].lexeme == "continue"
    assert types[1] == TokenType.SEMICOLON
    assert types[-1] == TokenType.EOF
