import ast
import argparse
import sys
from copy import deepcopy

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Measures coverage.')
	parser.add_argument('-v', '--verbose', action="store_true")
	parser.add_argument('-t', '--target', required=True)
	parser.add_argument("remaining", nargs="*")
	args = parser.parse_args()

	target = args.target
	lines = open(target, "r").readlines()
	root = ast.parse("".join(lines), target)
	
	# instrument the target script

	print("=====================================")
	print("Program Output")
	print("=====================================")
	
	# execute the instrumented target script

	print("=====================================")
	
	if args.verbose:
		print("=====================================")
		print("Covered Branches")
		# print verbose branch coverage
		print("=====================================")
		print("Covered Conditions")
		# print verbose condition coverage
	print("=====================================")