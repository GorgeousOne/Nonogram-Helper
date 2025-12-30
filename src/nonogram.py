# black white nonogram

import json
import os
import numpy as np

from state import State, Mark
import solve


def main():

	print(os.getcwd())
	with open('json/gram.json', 'r', encoding='utf-8') as f:
		json_str = json.load(f)
	gram = State.from_dict(json_str)
	solve.solve(gram)	
	print(gram)
	
if __name__ == '__main__':
	main()

	# gram = State(
	# 	1, 3, 
	# 	[[2]],
	# 	[[], [], []]
	# )
	# solve(gram)