# black white nonogram

from state import State, Mark
import numpy as np

def solve(gram:State):
	fill_initial(gram)


def fill_initial(gram:State):
	for row in range(gram.height):
		fill_initial_line(gram.clues_row[row], gram[row, :])
	for col in range(gram.width):
		fill_initial_line(gram.clues_col[col], gram[:, col])


def fill_idk_stuff(clue, line):
	splits = split_line(line)
	clue_len = sum(clue) + len(clue) - 1
	clue_line_diff = len(line) - clue_len
	avail_len = splits_len(splits)

import math

def gen_perms(clue, line_len):
	clue_len = get_clue_len(clue)
	diff = line_len - clue_len

	num_clues = len(clue)
	num_freedoms = num_clues + diff
	# unordered sampling w/o replacement
	num_perms = (
		math.factorial(num_freedoms)
		// (math.factorial(num_freedoms - num_clues)
			* math.factorial(num_clues)))
	idxs = [int(np.sum(clue[:i])) + i for i in range(num_clues)]
	perms = []
	for _ in range(num_perms):
		perm = np.zeros((line_len), dtype=np.byte)
		perms.append(perm)

		for i in range(num_clues):
			perm[idxs[i]:idxs[i]+clue[i]] = Mark.FULL.value
		# line = '-' * line_len
		# for i in range(num_clues):
		# 	j = int(idxs[i])
		# 	k = int(clue[i])
		# 	line = line[:j] + '#'*k + line[j+k:]
		# print(line)
		
		for x in range(num_clues-1, -1, -1):
			new_end = idxs[x] + clue[x] + 1
			if new_end <= line_len and (x == num_clues-1 or new_end < idxs[x+1]):
				idxs[x] += 1
				for y in range(x+1, num_clues):
					idxs[y] = idxs[y-1] + clue[y-1] + 1
				break
	return perms


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
		for j in range(i, i + num + diff):
			if line[j] == Mark.FREE.value:
				line[j] = Mark.PERHAPS.value
		for j in range(i + diff, i + num):
			line[j] = Mark.FULL.value
		i += num
		if i < len(line) and diff == 0:
			line[i] = Mark.AXED.value
		i += 1

def split_line(line):
	idx = np.where(line == Mark.AXED.value)[0]
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


print(gen_perms([3, 7, 2], 25))
