from lox.lox import is_complete_source
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.resolver import Resolver
from lox.scanner import Scanner


def run_with_interpreter(interpreter: Interpreter, source: str, capsys):
	scanner = Scanner(source)
	tokens = scanner.scan_tokens()
	parser = Parser(tokens)
	stmts = parser.parse()
	interpreter.locals.clear()
	Resolver(interpreter).resolve(stmts)
	interpreter.interpret(stmts)
	captured = capsys.readouterr()
	return captured.out.strip().splitlines()


def test_multiline_block_detection_and_execution(capsys):
	lines = [
		"if (true) {",
		"  var x = 1;",
		"  print x;",
		"}",
	]

	buffer = ""
	for i, line in enumerate(lines):
		buffer += line + "\n"
		if i < len(lines) - 1:
			assert not is_complete_source(buffer)
	assert is_complete_source(buffer)

	interp = Interpreter()
	out = run_with_interpreter(interp, buffer, capsys)
	assert out == ["1"]


def test_multiline_parentheses_and_semicolon(capsys):
	lines = [
		"print (1 +",
		"2);",
	]
	buffer = ""
	for i, line in enumerate(lines):
		buffer += line + "\n"
		if i == 0:
			assert not is_complete_source(buffer)
	assert is_complete_source(buffer)

	interp = Interpreter()
	out = run_with_interpreter(interp, buffer, capsys)
	assert out == ["3"]
