# monochrome nonogram

from collections import deque

from tree import PatternTree
from nono_math import calc_clue_len
from grid import Grid, FREE, FULL, AXED
from typing import Dict, Tuple, List

import time


def solve(grid:Grid):
	'''Solve a given (empty) nonogram grid'''
	trees = {}

	start = time.perf_counter()
	for line_id in grid.line_ids.keys():
		trees[line_id] = PatternTree(line_id, grid.get_clue(line_id), grid.get_line_len(line_id))
	end = time.perf_counter()
	print('nodes, edges:', count_tree_sizes(trees))
	print(f'gen trees {end-start:.3f}s')

	start = time.perf_counter()
	initialize_grid(grid, trees)
	solve_free_cells(grid, trees)
	end = time.perf_counter()
	print(f'solve {end-start:.3f}s')


def count_tree_sizes(trees:Dict[Tuple[str,int],PatternTree]):
	'''Count nodes & edges in tree structures to represent solver for this nonogram'''
	nodes = 0
	edges = 0
	for tree in trees.values():
		nodes += tree._node_count
		for l in tree._levels:
			for n in l.nodes:
				edges += len(n.children)
	return nodes, edges


def get_cross_line(line_id, cell):
	'''Returns the line id crossing a given line at a cell'''
	return ('R', cell) if 'C' in line_id else ('C', cell)


def initialize_grid(grid:Grid, trees:Dict[Tuple[str,int],PatternTree]):
	for line_id in grid.line_ids.keys():
		initialize_line(grid.get_clue(line_id), grid.get_line(line_id), line_id, trees[line_id], trees)

	if grid.is_symmetrical_horz():
		initialize_symmetry(grid, [l for l in grid.line_ids.keys() if 'R' in l], trees)
	elif grid.is_symmetrical_vert():
		initialize_symmetry(grid, [l for l in grid.line_ids.keys() if 'C' in l], trees)


def initialize_line(clue, line, line_id, tree:PatternTree, trees:Dict[Tuple[str,int],PatternTree]):
	# get mimimum length of clues combined
	clue_len = calc_clue_len(clue)
	# get possible offset
	diff = len(line) - clue_len
	i = 0
	# fill possible space and
	j = line_id[1]
	for num in clue:
		for k in range(i + diff, i + num):
			line[k] = FULL
			new_id = get_cross_line(line_id, k)
			tree.set_cell_full(k)
			trees[new_id].set_cell_full(j)
		i += num
		if i < len(line) and diff == 0:
			line[i] = AXED
			new_id = get_cross_line(line_id, i)
			tree.set_cell_axed(i)
			trees[new_id].set_cell_axed(j)
		i += 1

def initialize_symmetry(grid:Grid, line_ids:List[Tuple[str,int]], trees:Dict[Tuple[str,int],PatternTree]):
	line_len = grid.get_line_len(line_ids[0])

	for line_id in line_ids:
		line = grid.get_line(line_id)
		clue = grid.get_clue(line_id)
		clue_len = len(clue)
		tree = trees[line_id]
		if clue_len % 2 == 0:
			for i in range(line_len//2-1, line_len//2+1):
				line[i] = AXED
				tree.set_cell_axed(i)
		else:
			block = clue[clue_len//2]
			for i in range(line_len//2 - block//2, line_len//2 + block//2):
				line[i] = FULL
				tree.set_cell_full(i)
			for i in [line_len//2 - block//2 - 1, line_len//2 + block//2]:
				line[i] = AXED
				tree.set_cell_axed(i)


def solve_free_cells(grid:Grid, trees:Dict[Tuple[str,int],PatternTree]):
	queue = deque()
	queue.extend(grid.line_ids.keys())

	counter = 0
	while(queue):
		counter += 1

		line_id = queue.popleft()
		line = grid.get_line(line_id)
		tree = trees[line_id]

		for i in range(line.shape[0]):
			if line[i] != FREE:
				continue
			new_id = get_cross_line(line_id, i)
			j = line_id[1]
			if tree.do_all_patterns_cover(i):
				line[i] = FULL
				tree.set_cell_full(i)
				trees[new_id].set_cell_full(j)
				if new_id not in queue:
					queue.append(new_id)
				if line_id not in queue:
					queue.append(line_id)
			elif tree.do_all_patterns_avoid(i):
				line[i] = AXED
				tree.set_cell_axed(i)
				trees[new_id].set_cell_axed(j)
				if new_id not in queue:
					queue.append(new_id)
				if line_id not in queue:
					queue.append(line_id)
		if grid.is_complete():
			break

	if not grid.is_complete():
		print('mhh that didnt work :(')
	print(counter, 'iters')


def main():
	import json
	import sys
	json_path = sys.argv[1]

	with open(json_path, 'r', encoding='utf-8') as f:
		json_val = json.load(f)

	grid = Grid.from_dict(json_val)
	solve(grid)
	# print(grid)

	# save_path = json_path.replace('.json', '_solved.json')
	# with open(save_path, 'w', encoding='utf-8') as f:
	# 	json.dump(grid.to_dict(), f)

def debug():
	tr = PatternTree(('R', 0), [1,1,4,3,3,1,2,2,2,1,1,4,3,4,5,3], 70)
	start = time.perf_counter()
	tr.set_cell_axed(0)
	end = time.perf_counter()
	print(f'ax cell {end-start:.4f}s')

	print(tr._count_tree_size())
	print(tr._num_patterns)


if __name__ == '__main__':
	main()
	# debug()
