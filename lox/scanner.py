from typing import List

from lox.token import Token


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source

    def scan_tokens(self) -> List[Token]:
        tokens = []
        # Tokenization logic goes here
        return tokens
