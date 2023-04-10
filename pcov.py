import ast
import argparse
import sys, subprocess
import traceback
from copy import deepcopy

exec_lines = set()


def trace_file_execution(file_name, args):
    with open(file_name) as f:
        code = compile(f.read(), file_name, 'exec')
    lines_executed = set()

    def trace_lines(frame, event, arg):
        if event == 'line':
            line_no = frame.f_lineno
            if line_no not in exec_lines:
                exec_lines.add(line_no)
        return trace_lines

    try:
        sys.settrace(trace_lines)
        sys.argv = [file_name] + args
        exec(code, {})
    except:
        traceback.print_exc()
    finally:
        sys.settrace(None)

    return

BRANCHES_COUNT = 0
CONDITIONS_COUNT = 0
lines_with_stm = set()
br_nodes = [ast.If, ast.For, ast.While, ast.IfExp, ast.ListComp]

class MyVisitor(ast.NodeVisitor):
	def generic_visit(self, node):
		global BRANCHES_COUNT
		if isinstance(node, ast.stmt):
			lines_with_stm.add(node.lineno)
		if type(node) in br_nodes:
			BRANCHES_COUNT += 2
		if type(node) == ast.Try:
			BRANCHES_COUNT += len(node.handlers)
		super().generic_visit(node)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Measures coverage.')
	parser.add_argument('-v', '--verbose', action="store_true")
	parser.add_argument('-t', '--target', required=True)
	parser.add_argument("remaining", nargs="*")
	args = parser.parse_args()

	target = args.target
	lines = open(target, "r").readlines()
	root = ast.parse("".join(lines), target)
	visitor = MyVisitor()
	visitor.visit(root)
	# instrument the target script

	print("=====================================")
	print("Program Output")
	print("=====================================")
	
	
	# execute the instrumented target script
	trace_file_execution(target, args.remaining)

	executed_statements = len(lines_with_stm.intersection(exec_lines))

	all_statements = len(lines_with_stm)
    
	val = 0
	if all_statements != 0:
		val = (executed_statements/all_statements) * 100

	print("=====================================")
	print(f"Statement Coverage: {val:.2f}% ({executed_statements} / {all_statements})")
	print(f"Branch Coverage: {0.00}% (0 / {BRANCHES_COUNT})")
	print(f"Condition Coverage: {0.00}% (0 / {CONDITIONS_COUNT})")

	if args.verbose:
		print("=====================================")
		print("Covered Branches")
		# print verbose branch coverage
		print("=====================================")
		print("Covered Conditions")
		# print verbose condition coverage
	print("=====================================")