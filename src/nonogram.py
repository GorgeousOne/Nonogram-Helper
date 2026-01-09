# black white nonogram

import json
import os

from state import State
import solve


def main():

	print(os.getcwd())
	with open('json/gram.json', 'r', encoding='utf-8') as f:
		json_str = json.load(f)
	gram = State.from_dict(json_str)
	solve.solve(gram)
	print('welp')

if __name__ == '__main__':
	main()

	# gram = State(
	# 	1, 3,
	# 	[[2]],
	# 	[[], [], []]
	# )
	# solve(gram)