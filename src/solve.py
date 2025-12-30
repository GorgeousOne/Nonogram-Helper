# black white nonogram

from state import State, Mark
import numpy as np

def solve(gram:State):
	fill_initial(gram)


def fill_initial(gram:State):
	for row in range(gram.height):
		fill_initial_line(gram.rules_row[row], gram[row, :])
	for col in range(gram.width):
		fill_initial_line(gram.rules_col[col], gram[:, col])


def fill_idk_stuff(rule, line):
	splits = split_line(line)
	rule_len = sum(rule) + len(rule) - 1
	rule_line_diff = len(line) - rule_len
	avail_len = splits_len(splits)


def splits_len(splits):
	return np.sum(splits[:, 1] - splits[:, 0])

def fill_initial_line(rule, line):
	# get mimimum length of rules combined
	rule_len = sum(rule) + len(rule) - 1
	# get possible offset
	diff = len(line) - rule_len
	i = 0
	# fill possible space and 
	for num in rule:
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