# monochrome nonogram

import numpy as np
from collections import deque
from tqdm import tqdm

from tree import PlacementTree
from state import State, FREE, FULL, AXED
from typing import Dict

import time

def solve(gram:State):
	trees = {}

	start = time.perf_counter()
	for line_id in gram.line_ids.keys():
		trees[line_id] = PlacementTree(line_id, gram.get_clue(line_id), gram.get_len(line_id))
	end = time.perf_counter()
	print(f'gen trees {end-start:.3f}s')

	start = time.perf_counter()
	fill_initial_state(gram, trees)
	compare_lines(gram, trees)
	end = time.perf_counter()
	print(f'solve {end-start:.3f}s')
	print(gram)


def compare_lines(gram:State, trees:Dict[str,PlacementTree]):
	queue = deque()
	queue.extend(gram.line_ids.keys())

	counter = 0
	while(queue):
		counter += 1

		line_id = queue.popleft()
		line = gram.get_line(line_id)
		tree = trees[line_id]

		for i in range(line.shape[0]):
			if line[i] != FREE:
				continue
			# print('---', line_id, i)
			# print(tree.debug_nodes())
			if tree.do_all_paths_cover(i):
				line[i] = FULL
				new_id = f'R{i}' if 'C' in line_id else f'C{i}'
				j = int(line_id[1:])
				tree.set_pos_full(i)
				trees[new_id].set_pos_full(j)
				# print('fill', line_id, i)
				if new_id not in queue:
					queue.append(new_id)
				# if new_id not in queue:
				# 	queue.append(line_id)
			elif tree.do_all_paths_avoid(i):
				line[i] = AXED
				new_id = f'R{i}' if 'C' in line_id else f'C{i}'
				j = int(line_id[1:])
				tree.set_pos_axed(i)
				trees[new_id].set_pos_axed(j)
				# print('ax', line_id, i)
				if new_id not in queue:
					queue.append(new_id)
				# if new_id not in queue:
				# 	queue.append(line_id)

		# print(queue)
		if gram.is_complete():
			break

	if not gram.is_complete():
		print('mhh that didnt work :(')
		breakpoint()

def fill_initial_state(gram:State, trees:Dict[str,PlacementTree]):
	for line_id in gram.line_ids.keys():
		fill_initial_line(gram.get_clue(line_id), gram.get_line(line_id), line_id, trees[line_id], trees)


def get_clue_len(clue):
	return sum(clue) + len(clue) - 1


def fill_initial_line(clue, line, line_id, tree:PlacementTree, trees:Dict[str,PlacementTree]):
	# get mimimum length of clues combined
	clue_len = get_clue_len(clue)
	# get possible offset
	diff = len(line) - clue_len
	i = 0
	# fill possible space and
	j = int(line_id[1:])
	for num in clue:
		for k in range(i + diff, i + num):
			line[k] = FULL
			# print(gram)
			new_id = f'R{k}' if 'C' in line_id else f'C{k}'
			tree.set_pos_full(k)
			trees[new_id].set_pos_full(j)
		i += num
		if i < len(line) and diff == 0:
			line[i] = AXED
			# print(gram)
			new_id = f'R{i}' if 'C' in line_id else f'C{i}'
			tree.set_pos_axed(i)
			trees[new_id].set_pos_axed(j)

		i += 1

if __name__ == '__main__':
	import json
	import sys
	json_path = sys.argv[1]

	with open(json_path, 'r', encoding='utf-8') as f:
		json_val = json.load(f)

	gram = State.from_dict(json_val)
	solve(gram)
