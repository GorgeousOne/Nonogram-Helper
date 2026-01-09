# monochrome nonogram

from state import State, FREE, FULL, AXED
import numpy as np
from collections import deque

def solve(gram:State):
	fill_initial_state(gram)
	compare_lines(gram)

def compare_lines(gram:State):
	queue = deque()
	queue.extend(gram.line_ids.keys())

	permuations = {}
	for line_id in gram.line_ids.keys():
		permuations[line_id] = gen_perms(gram.get_clue(line_id), gram.width if 'R' in line_id else gram.height)
	import time
	while(queue):
		line_id = queue.popleft()
		line = gram.get_line(line_id)
		perms = permuations[line_id]

		# mask away contradicting permutations (rows)
		invalid_full = (perms == FULL) & (line == AXED)
		invalid_axed = (perms == AXED) & (line == FULL)
		valid_mask = ~np.any(invalid_full | invalid_axed, axis=1)
		perms = perms[valid_mask]

		for i in range(line.shape[0]):
			if np.all(perms[:, i] == perms[0, i]):
				line[i] = perms[0, i]
				# print(line_id, i, line[i])
				new_id = f'R{i}' if 'C' in line_id else f'C{i}'
				if new_id not in queue:
					queue.append(new_id)

		print(gram)
		permuations[line_id] = perms
		# time.sleep(2)
	print(gram)


def fill_initial_state(gram:State):
	for line_id in gram.line_ids.keys():
		fill_initial_line(gram.get_clue(line_id), gram.get_line(line_id))


def splits_len(splits):
	return np.sum(splits[:, 1] - splits[:, 0])


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


def split_line(line):
	idx = np.where(line == AXED)[0]
	prev = 0
	chunks = []
	for i in idx:
		if i > prev:
			chunks.append((prev, i))
		prev = i+1
	last = len(line)
	if last > prev:
		chunks.append((prev, last))
	return np.array(chunks)


def gen_perms(clue, line_len):
	# mark a block
	def place_block(start, size):
		arr = np.zeros(line_len, dtype=np.byte)
		arr[start:start + size] = FULL
		return arr

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
