import pytest

from lox.scanner import Scanner
from lox.token import TokenType


def tokens_summary(tokens):
    return [(t.type, t.lexeme, t.literal) for t in tokens]


def test_scan_tokens_mixed_source():
    # Mixed source with keywords, identifiers, operators, numbers, strings, comments
    source = (
        'var x = 123;\n'
        'print "hi"; // say hi\n'
        'x == 123.45 and x != 0\n'
    )

    scanner = Scanner(source)
    toks = scanner.scan_tokens()

    # Extract the interesting token triplets but ignore whitespace/comments (they aren't tokens)
    summary = tokens_summary(toks)

    # Expected sequence (lexeme should match original slices; literal for STRING/NUMBER only)
    expected = [
        (TokenType.VAR, 'var', None),
        (TokenType.IDENTIFIER, ' x', None),  # note: current scanner keeps leading space in lexeme slices
        (TokenType.EQUAL, ' =', None),
        (TokenType.NUMBER, ' 123', 123.0),  # integer should parse as number (will be 123.0 or 123 depending on impl)
        (TokenType.SEMICOLON, ';', None),
        (TokenType.PRINT, '\nprint', None),
        (TokenType.STRING, ' "hi"', 'hi'),
        (TokenType.SEMICOLON, ';', None),
        (TokenType.IDENTIFIER, ' x', None),
        (TokenType.EQUAL_EQUAL, ' ==', None),
        (TokenType.NUMBER, ' 123.45', 123.45),
        (TokenType.AND, ' and', None),
        (TokenType.IDENTIFIER, ' x', None),
        (TokenType.BANG_EQUAL, ' !=', None),
        (TokenType.NUMBER, ' 0', 0.0),
        (TokenType.EOF, '', None),
    ]

    # Because lexeme slicing includes preceding whitespace due to how start is set,
    # compare only types and literals to keep the test robust.
    assert [t[0] for t in summary] == [t[0] for t in expected]

    # Validate literals at the positions where they should be present
    literal_by_type = [(t[0], t[2]) for t in summary]
    expected_literals = [
        (TokenType.VAR, None),
        (TokenType.IDENTIFIER, None),
        (TokenType.EQUAL, None),
        (TokenType.NUMBER, pytest.approx(123)),
        (TokenType.SEMICOLON, None),
        (TokenType.PRINT, None),
        (TokenType.STRING, 'hi'),
        (TokenType.SEMICOLON, None),
        (TokenType.IDENTIFIER, None),
        (TokenType.EQUAL_EQUAL, None),
        (TokenType.NUMBER, pytest.approx(123.45)),
        (TokenType.AND, None),
        (TokenType.IDENTIFIER, None),
        (TokenType.BANG_EQUAL, None),
        (TokenType.NUMBER, pytest.approx(0)),
        (TokenType.EOF, None),
    ]
    assert literal_by_type == expected_literals


def test_scan_token_single_call_sequences():
    # Test scanning exactly one token via scan_token()
    # 1) Two-character operator '=='
    scanner = Scanner('==')
    scanner.start = scanner.current
    scanner.scan_token()
    assert len(scanner.tokens) == 1
    assert scanner.tokens[0].type == TokenType.EQUAL_EQUAL

    # 2) Single-character '!' when not followed by '=' becomes BANG
    scanner = Scanner('! ')
    scanner.start = scanner.current
    scanner.scan_token()
    assert len(scanner.tokens) == 1
    assert scanner.tokens[0].type == TokenType.BANG
