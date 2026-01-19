import math


def calc_clue_len(clue):
	return sum(clue) + len(clue) - 1


def calc_num_patterns(clue, line_len):
	clue_len = calc_clue_len(clue)
	diff = line_len - clue_len
	num_clues = len(clue)
	num_freedoms = num_clues + diff
	# unordered sampling w/o replacement
	num_patterns = (
		math.factorial(num_freedoms) // (
		math.factorial(num_freedoms - num_clues) * math.factorial(num_clues)))
	return num_patterns
