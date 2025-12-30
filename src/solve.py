# black white nonogram

from state import State, Mark
import numpy as np

def solve(gram:State):
	fill_inital(gram)


def fill_inital(gram:State):
	for row in range(gram.height):
		fill_initial_line(gram.rules_row[row], gram[row, :])
	for col in range(gram.width):
		fill_initial_line(gram.rules_col[col], gram[:, col])


def fill_initial_line(rule, line):
	rule_len = sum(rule) + len(rule) - 1
	diff = len(line) - rule_len
	i = 0
	for num in rule:
		for j in range(i, i + num + diff):
			line[j] = Mark.PERHAPS.value
		for j in range(i + diff, i + num):
			line[j] = Mark.FULL.value
		i += num + 1

def split_line(line):
	idx = np.where(line == Mark.AXED.value)[0]
	# im not fucking around with np.split forever to skip the splitting indices
	# fuck you
	prev = 0
	chunks = []
	for i in idx:
		chunks.append(line[prev:i])
		prev = i+1
	chunks.append(line[prev:len(line)])
	chunks = [c for c in chunks if len(c)]
	return chunks