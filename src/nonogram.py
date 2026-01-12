# monochrome nonogram

import json
import os

from state import State
import solve_perms

def main(json_path):
	print(os.getcwd())

	with open(json_path, 'r', encoding='utf-8') as f:
		json_val = json.load(f)

	gram = State.from_dict(json_val)
	solve_perms.solve(gram)

	with open(json_path.replace('.', '_solved.'), 'w', encoding='utf-8') as f:
		json.dump(gram.to_dict(), f, indent=2)
	print('welp')

if __name__ == '__main__':
	# main('json/bird.json')
	# main('json/night.json')
	# main('json/lamp.json')
	main('json/lighthouse.json')