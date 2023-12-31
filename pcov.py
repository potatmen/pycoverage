import ast
import argparse
import sys
from copy import deepcopy
import random
exec_lines = list()
if_stmt = dict()
cond_taken = set()
def trace_file_execution(file_name, args):
    with open(file_name) as f:
        code = compile(f.read(), file_name, 'exec')

    def trace_lines(frame, event, arg):
        if event == 'line':
            line_no = frame.f_lineno
            if line_no:
                exec_lines.append(line_no)
            if line_no in if_stmt:
                globals_ = frame.f_globals
                locals_ = frame.f_locals 
                code_object = compile(ast.Expression(if_stmt[line_no]), '<ast>', 'eval')
                res = eval(code_object, globals_, locals_)
                cond_taken.add((line_no, res))

        return trace_lines

    sys.settrace(trace_lines)
    sys.argv = [file_name] + args
    exec(code, {})
    sys.settrace(None)

    return

BRANCHES_COUNT = 0
CONDITIONS_COUNT = 0
lines_with_stm = set()
lines_with_branch = set()
exceptions = set()
br_nodes = [ast.If, ast.For, ast.While, ast.IfExp, ast.ListComp]

class MyVisitor(ast.NodeVisitor):
	
	def generic_visit(self, node):
		global BRANCHES_COUNT, CONDITIONS_COUNT
			
		if isinstance(node, ast.stmt):
			lines_with_stm.add(node.lineno)
		if type(node) in br_nodes:
            
			BRANCHES_COUNT += 2
        	
			lines_with_branch.add(node.lineno)
        
		if type(node) == ast.Try:
			BRANCHES_COUNT += len(node.handlers)
		
		if type(node) == ast.ExceptHandler:
			exceptions.add(node.lineno)
		
		if type(node) == ast.If or type(node) == ast.While or type(node) == ast.IfExp:
			if type(node.test) == ast.Compare:
				CONDITIONS_COUNT += 2 * len(node.test.ops)
			elif type(node.test) == ast.BoolOp:
				CONDITIONS_COUNT += 2 * len(node.test.values)
			if_stmt[node.lineno] = node.test
		if type(node) == ast.comprehension:
			CONDITIONS_COUNT += 2 * len(node.ifs)	
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
                  

	#print("Exec lines: " , exec_lines)
    
	#print("Branch lines: " , lines_with_branch)

	executed_statements = len(lines_with_stm.intersection(set(exec_lines)))

	all_statements = len(lines_with_stm)
    
	stm_prc = 0
	if all_statements != 0:
		stm_prc = (executed_statements/all_statements) * 100
                
	pairs = set()
	
	exec_branches = 0

	for i in range(len(exec_lines)):
    	
		if exec_lines[i] in lines_with_branch:
			if i + 1 < len(exec_lines):
				pairs.add((exec_lines[i], exec_lines[i + 1]))
			else:
				pairs.add((exec_lines[i], None))
		elif exec_lines[i] in exceptions and i + 1 < len(exec_lines) and exec_lines[i + 1] == exec_lines[i] + 1:
			pairs.add((exec_lines[i], exec_lines[i + 1]))

	
	exec_branches = len(pairs)
	res = random.randrange(1, )
	bra_prc = 0
	if BRANCHES_COUNT != 0:
		bra_prc = (exec_branches/BRANCHES_COUNT) * 100
	conds = len(cond_taken)
	cond_prc = 0
	if CONDITIONS_COUNT != 0:
		cond_prc = (conds /CONDITIONS_COUNT) * 100
	print("=====================================")
	if all_statements != 0: 
		print(f"Statement Coverage: {stm_prc:.2f}% ({executed_statements} / {all_statements})")
	if BRANCHES_COUNT != 0:
		print(f"Branch Coverage: {bra_prc:.2f}% ({exec_branches} / {BRANCHES_COUNT})")
	if CONDITIONS_COUNT != 0:
		print(f"Condition Coverage: {cond_prc:.2f}% ({conds} / {CONDITIONS_COUNT})")

	if args.verbose:
		print("=====================================")
		print("Covered Branches")
		# print verbose branch coverage
		print("=====================================")
		print("Covered Conditions")
		# print verbose condition coverage
	print("=====================================")