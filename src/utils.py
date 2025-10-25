import logging
import os

logger = logging.getLogger(__name__)


def validate_args(args):
    """Validate CLI arguments.

    Rules:
    - Only an optional positional FILE is supported; if provided, ensure it exists.
    - With no FILE, we default to REPL mode.
    """

    positional = getattr(args, "file", None)
    if positional is not None and not os.path.isfile(positional):
        raise FileNotFoundError(f"The file at path '{positional}' does not exist.")

    logger.debug(f"Args validated. file={positional}")


def is_complete_source(source: str) -> bool:
    """Heuristic check to see if the given source is a complete Lox input.

    Rules (basic, not string-aware):
    - Track parentheses and braces balance across lines.
    - Consider input complete when both balances are zero AND the last
      non-comment, non-whitespace significant character is ';' or '}'.
    """
    paren = 0
    brace = 0
    last_sig = ""

    for raw_line in source.splitlines():
        line = raw_line.split("//", 1)[0]
        paren += line.count("(") - line.count(")")
        brace += line.count("{") - line.count("}")
        s = line.rstrip()
        if s:
            last_sig = s[-1]

    if paren == 0 and brace == 0 and last_sig in {";", "}"}:
        return True
    return False
