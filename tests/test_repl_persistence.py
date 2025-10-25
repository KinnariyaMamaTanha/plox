from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.resolver import Resolver
from lox.scanner import Scanner


def run_with_interpreter(interpreter: Interpreter, source: str, capsys):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    stmts = parser.parse()
    # Clear any prior locals resolution info before resolving new AST
    interpreter.locals.clear()
    Resolver(interpreter).resolve(stmts)
    interpreter.interpret(stmts)
    captured = capsys.readouterr()
    return captured.out.strip().splitlines()


def test_vars_persist_across_runs(capsys):
    interp = Interpreter()
    out1 = run_with_interpreter(interp, "var a = 1;", capsys)
    assert out1 == []  # declaration prints nothing
    out2 = run_with_interpreter(interp, "print a;", capsys)
    assert out2 == ["1"]
