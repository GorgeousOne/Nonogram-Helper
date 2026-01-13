# monochrome nonogram

import numpy as np
from collections import deque

from state import State, FREE, FULL, AXED
import time

def solve(gram:State):
	permutations = {}

	from tqdm import tqdm
	start = time.perf_counter()
	for line_id in tqdm(gram.line_ids.keys()):
		permutations[line_id] = gen_perms(gram.get_clue(line_id), gram.get_len(line_id))
	end = time.perf_counter()
	print(f'gen perms {end-start:.3f}s')

	start = time.perf_counter()
	fill_initial_state(gram)
	compare_lines(gram, permutations)
	end = time.perf_counter()
	print(f'solve {end-start:.3f}s')


def compare_lines(gram:State, permutations):
	queue = deque()
	queue.extend(gram.line_ids.keys())

	complete = set()
	counter = 0

	while(queue):
		counter += 1

		line_id = queue.popleft()
		line = gram.get_line(line_id)
		perms = permutations[line_id]

		# mask away contradicting permutations (rows)
		invalid_full = (perms == FULL) & (line == AXED)
		invalid_axed = (perms == AXED) & (line == FULL)
		valid_mask = ~np.any(invalid_full | invalid_axed, axis=1)
		perms = perms[valid_mask]

		if perms.shape[0] == 0:
			raise Exception(f'no solution found for {line_id}, clue {gram.get_clue(line_id)}')

		for i in range(line.shape[0]):
			common_val = perms[0, i]
			# check out values all permutations agree on
			if not np.all(perms[:, i] == common_val):
				continue
			# check if undiscovered yet
			if line[i] == common_val:
				continue
			line[i] = common_val
			new_id = ('R', i) if 'C' in line_id else ('C', i)

			if new_id not in complete and new_id not in queue:
				queue.append(new_id)

		if np.all(line):
			complete.add(line_id)

		permutations[line_id] = perms
	# print(gram)
	print(counter, 'iters')


def fill_initial_state(gram:State):
	for line_id in gram.line_ids.keys():
		fill_initial_line(gram.get_clue(line_id), gram.get_line(line_id))


def get_clue_len(clue):
	return sum(clue) + len(clue) - 1


def fill_initial_line(clue, line):
	# get mimimum length of clues combined
	clue_len = get_clue_len(clue)
	# get possible offset
	diff = len(line) - clue_len
	i = 0
	# fill possible space and
	for num in clue:
		for j in range(i + diff, i + num):
			line[j] = FULL
		i += num
		if i < len(line) and diff == 0:
			line[i] = AXED
		i += 1


def gen_perms(clue, line_len):
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


if __name__ == '__main__':
	import json
	import sys
	json_path = sys.argv[1]

	with open(json_path, 'r', encoding='utf-8') as f:
		json_val = json.load(f)

	gram = State.from_dict(json_val)
	solve(gram)
	print(gram)
