from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.scanner import Scanner


def run_source(source: str, capsys):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    stmts = parser.parse()
    interp = Interpreter()
    interp.interpret(stmts)
    captured = capsys.readouterr()
    return captured.out.strip().splitlines()


def test_continue_in_while_skips_body_rest_and_continues(capsys):
    source = (
        "var i = 0;\n"
        "while (i < 5) {\n"
        "  i = i + 1;\n"
        "  if (i == 2 or i == 4) continue;\n"
        "  print i;\n"
        "}\n"
    )
    out_lines = run_source(source, capsys)
    assert out_lines == ["1", "3", "5"]
