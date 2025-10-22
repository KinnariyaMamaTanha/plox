from .tokentype import TokenType
class Token:
    def __init__(self) -> None:
        self.type: TokenType
        self.line: int
        self.lexeme: str
