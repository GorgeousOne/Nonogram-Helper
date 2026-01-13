# monochrome nonogram

import numpy as np
from collections import deque
from typing import Dict

from grid import Grid, FREE, FULL, AXED
import time

def solve(grid:Grid):
	pattern_list = {}
	print('total perms:', count_patterns(grid))

	# from tqdm import tqdm
	start = time.perf_counter()
	# for line_id in tqdm(grid.line_ids.keys()):
	for line_id in grid.line_ids.keys():
		pattern_list[line_id] = gen_line_patterns(grid.get_clue(line_id), grid.get_line_len(line_id))
	end = time.perf_counter()
	print(f'gen perms {end-start:.3f}s')

	start = time.perf_counter()
	initialize_grid(grid)
	solve_free_cells(grid, pattern_list)
	end = time.perf_counter()
	print(f'solve {end-start:.3f}s')


def count_patterns(grid:Grid):
	'''Precalculate number of patterns to generate in all lines'''
	import math
	total_perms = 0
	for line_id in grid.line_ids.keys():
		line_len = grid.get_line_len(line_id)
		clue = grid.get_clue(line_id)
		clue_len = get_clue_len(clue)
		diff = line_len - clue_len
		num_clues = len(clue)
		num_freedoms = num_clues + diff # unordered sampling w/o replacement
		num_perms = (
			math.factorial(num_freedoms) // (
				math.factorial(num_freedoms - num_clues) *
				math.factorial(num_clues)))
		if line_id == ('R', 3):
			print('r3', num_perms)

		total_perms += num_perms
	return total_perms


def get_clue_len(clue):
	return sum(clue) + len(clue) - 1


def initialize_grid(grid:Grid):
	for line_id in grid.line_ids.keys():
		initialize_line(grid.get_clue(line_id), grid.get_line(line_id))


def initialize_line(clue, line):
	# get mimimum length of clues combined
	clue_len = get_clue_len(clue)
	# get possible offset
	diff = len(line) - clue_len
	i = 0
	# fill possible space and
	for segment in clue:
		for j in range(i + diff, i + segment):
			line[j] = FULL
		i += segment
		if i < len(line) and diff == 0:
			line[i] = AXED
		i += 1


def gen_line_patterns(clue, line_len) -> np.ndarray:
	# recursively yields permutations
	def dfs(idx, pos, acc):
		# return array if no more clue blocks
		if idx == len(clue):
			yield acc
			return
		block = clue[idx]
		# calc range of possible block placements
		max_start = line_len - sum(clue[idx:]) - (len(clue) - idx - 1)
		# create variants with new block in all possible places
		for start in range(pos, max_start + 1):
			# merge existing perm part with new block
			new_acc = acc.copy()
			new_acc[start:start + block] = FULL
			yield from dfs(idx + 1, start + block + 1, new_acc)
	# collect yielded permutations as list
	return np.vstack(list(dfs(0, 0, np.full(line_len, AXED, dtype=np.byte))))


def solve_free_cells(grid:Grid, pattern_list:Dict[str, np.ndarray]):
	queue = deque()
	queue.extend(grid.line_ids.keys())

	complete = set()
	counter = 0

	while(queue):
		counter += 1

		line_id = queue.popleft()
		line = grid.get_line(line_id)
		patterns = pattern_list[line_id]

		# mask away contradicting permutations (rows)
		invalid_full = (patterns == FULL) & (line == AXED)
		invalid_axed = (patterns == AXED) & (line == FULL)
		valid_mask = ~np.any(invalid_full | invalid_axed, axis=1)
		patterns = patterns[valid_mask]

		if patterns.shape[0] == 0:
			raise Exception(f'no pattern found for {line_id}, clue {grid.get_clue(line_id)}')

		for i in range(line.shape[0]):
			fixed_cell = patterns[0, i]
			# check out cells all patterns agree on
			if not np.all(patterns[:, i] == fixed_cell):
				continue
			# check if undiscovered yet
			if line[i] == fixed_cell:
				continue
			line[i] = fixed_cell
			cross_line_id = ('R', i) if 'C' in line_id else ('C', i)

			if cross_line_id not in complete and cross_line_id not in queue:
				queue.append(cross_line_id)

		if np.all(line):
			complete.add(line_id)

		pattern_list[line_id] = patterns
	# print(grid)
	print(counter, 'iters')


def main():
	import json
	import sys
	json_path = sys.argv[1]

	with open(json_path, 'r', encoding='utf-8') as f:
		json_val = json.load(f)

	grid = Grid.from_dict(json_val)
	solve(grid)
	print(grid)

if __name__ == '__main__':
	main()