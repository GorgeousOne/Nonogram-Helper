# monochrome nonogram

from collections import deque

from tree import PatternTree
from grid import Grid, FREE, FULL, AXED
from typing import Dict, Tuple

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


def get_clue_len(clue):
	return sum(clue) + len(clue) - 1


def get_cross_line(line_id, cell):
	'''Returns the line id crossing a given line at a cell'''
	return ('R', cell) if 'C' in line_id else ('C', cell)


def initialize_grid(grid:Grid, trees:Dict[Tuple[str,int],PatternTree]):
	for line_id in grid.line_ids.keys():
		initialize_line(grid.get_clue(line_id), grid.get_line(line_id), line_id, trees[line_id], trees)


def initialize_line(clue, line, line_id, tree:PatternTree, trees:Dict[Tuple[str,int],PatternTree]):
	# get mimimum length of clues combined
	clue_len = get_clue_len(clue)
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
			elif tree.do_all_patterns_avoid(i):
				line[i] = AXED
				tree.set_cell_axed(i)
				trees[new_id].set_cell_axed(j)
				if new_id not in queue:
					queue.append(new_id)
		if grid.is_complete():
			break

	if not grid.is_complete():
		print('mhh that didnt work :(')
		breakpoint()
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