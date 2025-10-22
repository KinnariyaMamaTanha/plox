from lox.token import Token, TokenType


def test_token_str():
    token = Token(type=TokenType.IDENTIFIER, lexeme="varName", literal=None, line=1)
    assert str(token) == "TokenType.IDENTIFIER varName None"
