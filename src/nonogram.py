# monochrome nonogram

import json
import os

from state import State
import solve

def main(json_path):
	print(os.getcwd())
	with open(json_path, 'r', encoding='utf-8') as f:
		json_str = json.load(f)
	gram = State.from_dict(json_str)
	solve.solve(gram)
	print('welp')

if __name__ == '__main__':
	# main('json/bird.json')
	main('json/lamp.json')